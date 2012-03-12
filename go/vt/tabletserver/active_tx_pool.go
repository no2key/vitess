/*
Copyright 2012, Google Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the
distribution.
    * Neither the name of Google Inc. nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,           
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY           
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

package tabletserver

import (
	"code.google.com/p/vitess/go/relog"
	"code.google.com/p/vitess/go/stats"
	"code.google.com/p/vitess/go/timer"
	"fmt"
	"sync"
	"time"
)

/* Function naming convention:
UpperCaseFunctions() are thread safe, they can still panic on error
lowerCaseFunctions() are not thread safe
SafeFunctions() return os.Error instead of throwing exceptions
*/

var (
	BEGIN    = []byte("begin")
	COMMIT   = []byte("commit")
	ROLLBACK = []byte("rollback")
)

type ActiveTxPool struct {
	mu          sync.Mutex
	connections map[int64]*TxConnection
	capacity    int
	size        int
	lastId      int64
	timeout     time.Duration
	ticks       *timer.Timer
	txStats     *stats.Timings
}

func NewActiveTxPool(capacity int, timeout time.Duration) *ActiveTxPool {
	return &ActiveTxPool{
		capacity:    capacity,
		connections: make(map[int64]*TxConnection, capacity),
		lastId:      time.Now().UnixNano(),
		timeout:     timeout,
		ticks:       timer.NewTimer(timeout / 10),
		txStats:     stats.NewTimings("Transactions"),
	}
}

func (self *ActiveTxPool) Open() {
	relog.Info("Starting transaction id: %d", self.lastId)
	go self.TransactionKiller()
}

func (self *ActiveTxPool) Close() {
	self.ticks.Close()
	self.mu.Lock()
	defer self.mu.Unlock()

	// This should be empty. Just a failsafe.
	for tid, conn := range self.connections {
		conn.Smart().Close()
		self.discard(tid)
	}
}

func (self *ActiveTxPool) WaitForEmpty() {
	for self.Size() != 0 {
		// Inefficient but simple
		<-time.After(1e9)
	}
}

func (self *ActiveTxPool) TransactionKiller() {
	for self.ticks.Next() {
		for conn := self.ScanForTimeout(); conn != nil; conn = self.ScanForTimeout() {
			relog.Info("killing transaction %d", conn.TransactionId)
			killStats.Add("Transactions", 1)
			conn.Smart().Close()
			self.Discard(conn.TransactionId)
		}
	}
}

func (self *ActiveTxPool) ScanForTimeout() (conn *TxConnection) {
	self.mu.Lock()
	defer self.mu.Unlock()

	t := time.Now()
	for _, conn = range self.connections {
		if conn.InUse {
			continue
		}
		if conn.StartTime.Add(self.timeout).Sub(t) < 0 {
			conn.InUse = true
			return conn
		}
	}
	return nil
}

func (self *ActiveTxPool) SafeBegin(conn PoolConnection) (transactionId int64, err error) {
	defer handleError(&err)
	if _, err := conn.Smart().ExecuteFetch(BEGIN, 10000); err != nil {
		panic(NewTabletErrorSql(FAIL, err))
	}

	self.mu.Lock()
	defer self.mu.Unlock()
	self.lastId++
	self.connections[self.lastId] = NewTxConnection(conn, self.lastId, self)
	self.size++
	return self.lastId, nil
}

// An unpleasant dependency to SchemaInfo. Avoiding it makes the code worse
func (self *ActiveTxPool) Commit(transactionId int64, schemaInfo *SchemaInfo) {
	conn := self.Get(transactionId)
	defer self.Discard(transactionId)
	self.txStats.Add("Completed", time.Now().Sub(conn.StartTime))
	defer func() {
		for tableName, invalidList := range conn.DirtyTables {
			tableInfo := schemaInfo.GetTable(tableName)
			for key := range invalidList {
				tableInfo.RowCache.Delete(key)
			}
			schemaInfo.Put(tableInfo)
		}
	}()
	if _, err := conn.Smart().ExecuteFetch(COMMIT, 10000); err != nil {
		conn.Smart().Close()
		panic(NewTabletErrorSql(FAIL, err))
	}
}

func (self *ActiveTxPool) Rollback(transactionId int64) {
	conn := self.Get(transactionId)
	defer self.Discard(transactionId)
	self.txStats.Add("Aborted", time.Now().Sub(conn.StartTime))
	if _, err := conn.Smart().ExecuteFetch(ROLLBACK, 10000); err != nil {
		conn.Smart().Close()
		panic(NewTabletErrorSql(FAIL, err))
	}
}

func (self *ActiveTxPool) Get(transactionId int64) (conn *TxConnection) {
	self.mu.Lock()
	defer self.mu.Unlock()

	txConn, ok := self.connections[transactionId]
	if !ok {
		panic(NewTabletError(FAIL, "Transaction %d not found", transactionId))
	}
	if txConn.InUse {
		panic(NewTabletError(FAIL, "Connection for transaction %d is in use", transactionId))
	}
	txConn.InUse = true
	return txConn
}

func (self *ActiveTxPool) Put(transactionId int64) {
	self.mu.Lock()
	defer self.mu.Unlock()

	txConn, ok := self.connections[transactionId]
	if !ok {
		panic(NewTabletError(FAIL, "Transaction %d not found", transactionId))
	}
	if txConn.Smart().IsClosed {
		relog.Info("abandoning transaction %d", transactionId)
		killStats.Add("Transactions", 1)
		self.discard(transactionId)
	} else {
		txConn.InUse = false
	}
}

func (self *ActiveTxPool) Discard(transactionId int64) {
	self.mu.Lock()
	defer self.mu.Unlock()
	self.discard(transactionId)
}

func (self *ActiveTxPool) discard(transactionId int64) {
	conn, ok := self.connections[transactionId]
	if !ok {
		return
	}
	conn.InUse = false
	delete(self.connections, transactionId)
	self.size--
	conn.PoolConnection.Recycle()
}

func (self *ActiveTxPool) SetCapacity(capacity int) {
	if capacity <= 0 {
		panic(NewTabletError(FAIL, "Capacity out of range %d", capacity))
	}
	self.mu.Lock()
	defer self.mu.Unlock()
	self.capacity = capacity
}

func (self *ActiveTxPool) SetTimeout(timeout time.Duration) {
	self.mu.Lock()
	defer self.mu.Unlock()
	self.timeout = timeout
	self.ticks.SetInterval(timeout / 10)
}

func (self *ActiveTxPool) StatsJSON() string {
	s, c, t := self.Stats()
	return fmt.Sprintf("{\"Size\": %v, \"Capacity\": %v, \"Timeout\": %v}", s, c, float64(t)/1e9)
}

func (self *ActiveTxPool) Stats() (size, capacity int, timeout time.Duration) {
	self.mu.Lock()
	defer self.mu.Unlock()
	return self.size, self.capacity, self.timeout
}

func (self *ActiveTxPool) Size() int {
	self.mu.Lock()
	defer self.mu.Unlock()
	return int(self.size)
}

type TxConnection struct {
	PoolConnection
	TransactionId int64
	Pool          *ActiveTxPool
	InUse         bool
	StartTime     time.Time
	DirtyTables   map[string]DirtyKeys
}

func NewTxConnection(conn PoolConnection, transactionId int64, pool *ActiveTxPool) *TxConnection {
	return &TxConnection{
		PoolConnection: conn,
		TransactionId:  transactionId,
		Pool:           pool,
		StartTime:      time.Now(),
		DirtyTables:    make(map[string]DirtyKeys),
	}
}

func (self *TxConnection) DirtyKeys(tableName string) DirtyKeys {
	if list, ok := self.DirtyTables[tableName]; ok {
		return list
	}
	list := make(DirtyKeys)
	self.DirtyTables[tableName] = list
	return list
}

func (self *TxConnection) Recycle() {
	self.Pool.Put(self.TransactionId)
}

type DirtyKeys map[string]bool

// Delete just keeps track of what needs to be deleted
func (self DirtyKeys) Delete(key string) bool {
	self[key] = true
	return true
}