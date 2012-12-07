from cases_framework import Case, MultiCase

cases = [
    Case(doc='union',
         sql='select /* union */ eid, id from vtocc_a union select eid, id from vtocc_b',
         result=[(1L, 1L), (1L, 2L)],
         rewritten=[
           'select eid, id from vtocc_a where 1 != 1 union select eid, id from vtocc_b where 1 != 1',
           'select /* union */ eid, id from vtocc_a union select eid, id from vtocc_b']),

    Case(doc='double union',
         sql='select /* double union */ eid, id from vtocc_a union select eid, id from vtocc_b union select eid, id from vtocc_d',
         result=[(1L, 1L), (1L, 2L)],
         rewritten=[
           'select eid, id from vtocc_a where 1 != 1 union select eid, id from vtocc_b where 1 != 1 union select eid, id from vtocc_d where 1 != 1',
           'select /* double union */ eid, id from vtocc_a union select eid, id from vtocc_b union select eid, id from vtocc_d']),

    Case(doc="distinct",
         sql='select /* distinct */ distinct * from vtocc_a',
         result=[(1L, 1L, 'abcd', 'efgh'), (1L, 2L, 'bcde', 'fghi')],
         rewritten=[
           'select * from vtocc_a where 1 != 1',
           'select /* distinct */ distinct * from vtocc_a limit 10001']),

    Case(doc='group by',
         sql='select /* group by */ eid, sum(id) from vtocc_a group by eid',
         result=[(1L, 3L)],
         rewritten=[
           'select eid, sum(id) from vtocc_a where 1 != 1',
           'select /* group by */ eid, sum(id) from vtocc_a group by eid limit 10001']),
    Case(doc='having',
         sql='select /* having */ sum(id) from vtocc_a having sum(id) = 3',
         result=[(3L,)],
         rewritten=[
           'select sum(id) from vtocc_a where 1 != 1',
           'select /* having */ sum(id) from vtocc_a having sum(id) = 3 limit 10001']),

    Case(doc='limit',
         sql='select /* limit */ eid, id from vtocc_a limit %(a)s',
         bindings={"a": 1},
         result=[(1L, 1L)],
         rewritten=[
           'select eid, id from vtocc_a where 1 != 1',
           'select /* limit */ eid, id from vtocc_a limit 1']),
    Case(doc='multi-table',
         sql='select /* multi-table */ a.eid, a.id, b.eid, b.id  from vtocc_a as a, vtocc_b as b',
         result=[(1L, 1L, 1L, 1L), (1L, 2L, 1L, 1L), (1L, 1L, 1L, 2L), (1L, 2L, 1L, 2L)],
         rewritten=[
           'select a.eid, a.id, b.eid, b.id from vtocc_a as a, vtocc_b as b where 1 != 1',
           'select /* multi-table */ a.eid, a.id, b.eid, b.id from vtocc_a as a, vtocc_b as b limit 10001']),

    Case(doc='multi-table join',
         sql='select /* multi-table join */ a.eid, a.id, b.eid, b.id from vtocc_a as a join vtocc_b as b on a.eid = b.eid and a.id = b.id',
         result=[(1L, 1L, 1L, 1L), (1L, 2L, 1L, 2L)],
         rewritten=[
           'select a.eid, a.id, b.eid, b.id from vtocc_a as a join vtocc_b as b where 1 != 1',
           'select /* multi-table join */ a.eid, a.id, b.eid, b.id from vtocc_a as a join vtocc_b as b on a.eid = b.eid and a.id = b.id limit 10001']),


    Case(doc='complex select list',
         sql='select /* complex select list */ eid+1, id from vtocc_a',
         result=[(2L, 1L), (2L, 2L)],
         rewritten=[
           'select eid+1, id from vtocc_a where 1 != 1',
           'select /* complex select list */ eid+1, id from vtocc_a limit 10001']),
    Case(doc="*",
         sql='select /* * */ * from vtocc_a',
         result=[(1L, 1L, 'abcd', 'efgh'), (1L, 2L, 'bcde', 'fghi')],
         rewritten=[
           'select * from vtocc_a where 1 != 1',
           'select /* * */ * from vtocc_a limit 10001']),

    Case(doc='table alias',
         sql='select /* table alias */ a.eid from vtocc_a as a where a.eid=1',
         result=[(1L,), (1L,)],
         rewritten=[
           'select a.eid from vtocc_a as a where 1 != 1',
           'select /* table alias */ a.eid from vtocc_a as a where a.eid = 1 limit 10001']),

    Case(doc='parenthesised col',
         sql='select /* parenthesised col */ (eid) from vtocc_a where eid = 1 and id = 1',
         result=[(1L,)],
         rewritten=[
           'select eid from vtocc_a where 1 != 1',
           'select /* parenthesised col */ eid from vtocc_a where eid = 1 and id = 1 limit 10001']),

    MultiCase('for update',
              ['begin',
               Case(sql='select /* for update */ eid from vtocc_a where eid = 1 and id = 1 for update',
                    result=[(1L,)],
                    rewritten=[
                      'select eid from vtocc_a where 1 != 1',
                      'select /* for update */ eid from vtocc_a where eid = 1 and id = 1 limit 10001 for update']),
               'commit']),

    Case(doc='complex where',
         sql='select /* complex where */ id from vtocc_a where id+1 = 2',
         result=[(1L,)],
         rewritten=[
           'select id from vtocc_a where 1 != 1',
           'select /* complex where */ id from vtocc_a where id+1 = 2 limit 10001']),

    Case(doc='complex where (non-value operand)',
         sql='select /* complex where (non-value operand) */ eid, id from vtocc_a where eid = id',
         result=[(1L, 1L)],
         rewritten=[
           'select eid, id from vtocc_a where 1 != 1',
           'select /* complex where (non-value operand) */ eid, id from vtocc_a where eid = id limit 10001']),

    Case(doc='(condition)',
         sql='select /* (condition) */ * from vtocc_a where (eid = 1)',
         result=[(1L, 1L, 'abcd', 'efgh'), (1L, 2L, 'bcde', 'fghi')],
         rewritten=[
           'select * from vtocc_a where 1 != 1',
           'select /* (condition) */ * from vtocc_a where (eid = 1) limit 10001']),

    Case(doc='inequality',
         sql='select /* inequality */ * from vtocc_a where id > 1',
         result=[(1L, 2L, 'bcde', 'fghi')],
         rewritten=[
           'select * from vtocc_a where 1 != 1',
           'select /* inequality */ * from vtocc_a where id > 1 limit 10001']),
    Case(doc='in',
         sql='select /* in */ * from vtocc_a where id in (1, 2)',
         result=[(1L, 1L, 'abcd', 'efgh'), (1L, 2L, 'bcde', 'fghi')],
         rewritten=[
           'select * from vtocc_a where 1 != 1',
           'select /* in */ * from vtocc_a where id in (1, 2) limit 10001']),

    Case(doc='between',
         sql='select /* between */ * from vtocc_a where id between 1 and 2',
         result=[(1L, 1L, 'abcd', 'efgh'), (1L, 2L, 'bcde', 'fghi')],
         rewritten=[
           'select * from vtocc_a where 1 != 1',
           'select /* between */ * from vtocc_a where id between 1 and 2 limit 10001']),

    Case(doc='order',
         sql='select /* order */ * from vtocc_a order by id desc',
         result=[(1L, 2L, 'bcde', 'fghi'), (1L, 1L, 'abcd', 'efgh')],
         rewritten=[
           'select * from vtocc_a where 1 != 1',
           'select /* order */ * from vtocc_a order by id desc limit 10001']),
    Case(doc='select in select list',
         sql='select (select eid from vtocc_a where id = 1), eid from vtocc_a where id = 2',
         result=[(1L, 1L)],
         rewritten=[
           'select (select eid from vtocc_a where 1 != 1), eid from vtocc_a where 1 != 1',
           'select (select eid from vtocc_a where id = 1), eid from vtocc_a where id = 2 limit 10001']),
    Case(doc='select in from clause',
         sql='select eid from (select eid from vtocc_a where id=2) as a',
         result=[(1L,)],
         rewritten=[
           'select eid from (select eid from vtocc_a where 1 != 1) as a where 1 != 1',
           'select eid from (select eid from vtocc_a where id = 2) as a limit 10001']),

    MultiCase(
        'simple insert',
        ['begin',
         Case(sql="insert /* simple */ into vtocc_a values (2, 1, 'aaaa', 'bbbb')",
              result=[],
              rewritten="insert /* simple */ into vtocc_a values (2, 1, 'aaaa', 'bbbb') /* _stream vtocc_a (eid id ) (2 1 ); */"),
         'commit',
         Case(sql='select * from vtocc_a where eid = 2 and id = 1',
              result=[(2L, 1L, 'aaaa', 'bbbb')]),
         'begin',
         'delete from vtocc_a where eid>1',
         'commit']),

    MultiCase(
        'qualified insert',
        ['begin',
         Case(sql="insert /* qualified */ into vtocc_a(eid, id, name, foo) values (3, 1, 'aaaa', 'cccc')",
              rewritten="insert /* qualified */ into vtocc_a(eid, id, name, foo) values (3, 1, 'aaaa', 'cccc') /* _stream vtocc_a (eid id ) (3 1 ); */"),
         'commit',
         Case(sql='select * from vtocc_a where eid = 3 and id = 1',
              result=[(3L, 1L, 'aaaa', 'cccc')]),
         'begin',
         'delete from vtocc_a where eid>1',
         'commit']),

    MultiCase(
        'insert auto_increment',
        ['alter table vtocc_e auto_increment = 1',
         'begin',
         Case(sql="insert /* auto_increment */ into vtocc_e(name, foo) values ('aaaa', 'cccc')",
              rewritten="insert /* auto_increment */ into vtocc_e(name, foo) values ('aaaa', 'cccc') /* _stream vtocc_e (eid id name ) (null 1 'YWFhYQ==' ); */"),
         'commit',
         Case(sql='select * from vtocc_e',
              result=[(1L, 1L, 'aaaa', 'cccc')]),
         'begin',
         'delete from vtocc_e',
         'commit']),

    MultiCase(
        'insert with number default value',
        ['begin',
         Case(sql="insert /* num default */ into vtocc_a(eid, name, foo) values (3, 'aaaa', 'cccc')",
              rewritten="insert /* num default */ into vtocc_a(eid, name, foo) values (3, 'aaaa', 'cccc') /* _stream vtocc_a (eid id ) (3 1 ); */"),
         'commit',
         Case(sql='select * from vtocc_a where eid = 3 and id = 1',
              result=[(3L, 1L, 'aaaa', 'cccc')]),
         'begin',
         'delete from vtocc_a where eid>1',
         'commit']),

    MultiCase(
        'insert with string default value',
        ['begin',
         Case(sql="insert /* string default */ into vtocc_f(id) values (1)",
              rewritten="insert /* string default */ into vtocc_f(id) values (1) /* _stream vtocc_f (vb ) ('YWI=' ); */"),
         'commit',
         Case(sql='select * from vtocc_f',
              result=[('ab', 1)]),
         'begin',
         'delete from vtocc_f',
         'commit']),

    MultiCase(
        'bind values',
        ['begin',
         Case(sql="insert /* bind values */ into vtocc_a(eid, id, name, foo) values (%(eid)s, %(id)s, %(name)s, %(foo)s)",
              bindings={"eid": 4, "id": 1, "name": "aaaa", "foo": "cccc"},
              rewritten="insert /* bind values */ into vtocc_a(eid, id, name, foo) values (4, 1, 'aaaa', 'cccc') /* _stream vtocc_a (eid id ) (4 1 ); */"),
         'commit',
         Case(sql='select * from vtocc_a where eid = 4 and id = 1',
              result=[(4L, 1L, 'aaaa', 'cccc')]),
         'begin',
         'delete from vtocc_a where eid>1',
         'commit']),

    MultiCase(
        'out of sequence columns',
        ['begin',
         Case(sql="insert into vtocc_a(id, eid, foo, name) values (-1, 5, 'aaa', 'bbb')",
              rewritten="insert into vtocc_a(id, eid, foo, name) values (-1, 5, 'aaa', 'bbb') /* _stream vtocc_a (eid id ) (5 -1 ); */"),
         'commit',
         Case(sql='select * from vtocc_a where eid = 5 and id = -1',
              result=[(5L, -1L, 'bbb', 'aaa')]),
         'begin',
         'delete from vtocc_a where eid>1',
         'commit']),

    MultiCase(
        'expressions',
        ['begin',
         Case(sql="insert into vtocc_a(eid, id, name, foo) values (7, 1+1, '', '')",
              rewritten="insert into vtocc_a(eid, id, name, foo) values (7, 1+1, '', '')"),
         'commit',
         Case('select * from vtocc_a where eid = 7',
              result=[(7L, 2L, '', '')]),
         'begin',
         'delete from vtocc_a where eid>1',
         'commit']),

    MultiCase(
        'no index',
        ['begin',
         Case(sql="insert into vtocc_d(eid, id) values (1, 1)",
              rewritten="insert into vtocc_d(eid, id) values (1, 1)"),
         'commit',
         Case(sql='select * from vtocc_d',
              result=[(1L, 1L)]),
         'begin',
         'delete from vtocc_d',
         'commit']),

    MultiCase(
        'on duplicate key',
        ['begin',
         Case(sql="insert into vtocc_a(eid, id, name, foo) values (8, 1, '', '') on duplicate key update name = 'foo'",
              rewritten="insert into vtocc_a(eid, id, name, foo) values (8, 1, '', '') on duplicate key update name = 'foo' /* _stream vtocc_a (eid id ) (8 1 ); */",),
         'commit',
         Case(sql='select * from vtocc_a where eid = 8',
              result=[(8L, 1L, '', '')]),
         'begin',
         Case(sql="insert into vtocc_a(eid, id, name, foo) values (8, 1, '', '') on duplicate key update name = 'foo'",
              rewritten="insert into vtocc_a(eid, id, name, foo) values (8, 1, '', '') on duplicate key update name = 'foo' /* _stream vtocc_a (eid id ) (8 1 ); */"),
         'commit',
         Case(sql='select * from vtocc_a where eid = 8',
              result=[(8L, 1L, 'foo', '')]),
         'begin',
         Case(sql="insert into vtocc_a(eid, id, name, foo) values (8, 1, '', '') on duplicate key update id = 2",
              rewritten="insert into vtocc_a(eid, id, name, foo) values (8, 1, '', '') on duplicate key update id = 2 /* _stream vtocc_a (eid id ) (8 1 ) (8 2 ); */"),
         'commit',
         Case(sql='select * from vtocc_a where eid = 8',
              result=[(8L, 2L, 'foo', '')]),
         'begin',
         Case(sql="insert into vtocc_a(eid, id, name, foo) values (8, 2, '', '') on duplicate key update id = 2+1",
              rewritten="insert into vtocc_a(eid, id, name, foo) values (8, 2, '', '') on duplicate key update id = 2+1"),
         'commit',
         Case(sql='select * from vtocc_a where eid = 8',
              result=[(8L, 3L, 'foo', '')]),
         'begin',
         'delete from vtocc_a where eid>1',
         'commit']),

    MultiCase(
        'subquery',
        ['begin',
         Case(sql="insert /* subquery */ into vtocc_a(eid, name, foo) select eid, name, foo from vtocc_c",
              rewritten =[
                  'select eid, name, foo from vtocc_c limit 10001',
                  "insert /* subquery */ into vtocc_a(eid, name, foo) values (10, 'abcd', '20'), (11, 'bcde', '30') /* _stream vtocc_a (eid id ) (10 1 ) (11 1 ); */",
                  ]),
         'commit',
         Case(sql='select * from vtocc_a where eid in (10, 11)',
              result=[(10L, 1L, 'abcd', '20'), (11L, 1L, 'bcde', '30')]),
         'begin',
         Case(sql="insert into vtocc_a(eid, name, foo) select eid, name, foo from vtocc_c on duplicate key update foo='bar'",
              rewritten=[
                  'select eid, name, foo from vtocc_c limit 10001',
                  "insert into vtocc_a(eid, name, foo) values (10, 'abcd', '20'), (11, 'bcde', '30') on duplicate key update foo = 'bar' /* _stream vtocc_a (eid id ) (10 1 ) (11 1 ); */",
                  ]),
         'commit',
         Case(sql='select * from vtocc_a where eid in (10, 11)',
              result=[(10L, 1L, 'abcd', 'bar'), (11L, 1L, 'bcde', 'bar')]),
         'begin',
         Case(sql="insert into vtocc_a(eid, name, foo) select eid, name, foo from vtocc_c limit 1 on duplicate key update id = 21",
              rewritten=[
                  'select eid, name, foo from vtocc_c limit 1',
                  "insert into vtocc_a(eid, name, foo) values (10, 'abcd', '20') on duplicate key update id = 21 /* _stream vtocc_a (eid id ) (10 1 ) (10 21 ); */",
                  ]),
         'commit',
         Case(sql='select * from vtocc_a where eid in (10, 11)',
              result=[(10L, 21L, 'abcd', 'bar'), (11L, 1L, 'bcde', 'bar')]),
         'alter table vtocc_e auto_increment = 1',
         'begin',
         Case(sql='insert into vtocc_e(id, name, foo) select eid, name, foo from vtocc_c',
           rewritten=[
                  'select eid, name, foo from vtocc_c limit 10001',
                  "insert into vtocc_e(id, name, foo) values (10, 'abcd', '20'), (11, 'bcde', '30') /* _stream vtocc_e (eid id name ) (null 10 'YWJjZA==' ) (null 11 'YmNkZQ==' ); */",
             ]),
         'commit',
         Case(sql='select eid, id, name, foo from vtocc_e',
           result=[(1L, 10L, 'abcd', '20'), (2L, 11L, 'bcde', '30')]),
         'begin',
         'delete from vtocc_a where eid>1',
         'delete from vtocc_c where eid<10',
         'commit']),

    MultiCase(
        'multi-value',
        ['begin',
         Case(sql="insert into vtocc_a(eid, id, name, foo) values (5, 1, '', ''), (7, 1, '', '')",
              rewritten="insert into vtocc_a(eid, id, name, foo) values (5, 1, '', ''), (7, 1, '', '') /* _stream vtocc_a (eid id ) (5 1 ) (7 1 ); */"),
         'commit',
         Case(sql='select * from vtocc_a where eid>1',
              result=[(5L, 1L, '', ''), (7L, 1L, '', '')]),
         'begin',
         'delete from vtocc_a where eid>1',
         'commit']),

    MultiCase(
        'update',
        ['begin',
         Case(sql="update /* pk */ vtocc_a set foo='bar' where eid = 1 and id = 1",
              rewritten="update /* pk */ vtocc_a set foo = 'bar' where eid = 1 and id = 1 /* _stream vtocc_a (eid id ) (1 1 ); */"),
         'commit',
         Case(sql='select foo from vtocc_a where id = 1',
              result=[('bar',)]),
         'begin',
         "update vtocc_a set foo='efgh' where id=1",
         'commit']),


    MultiCase(
        'single in',
        ['begin',
         Case(sql="update /* pk */ vtocc_a set foo='bar' where eid = 1 and id in (1, 2)",
              rewritten="update /* pk */ vtocc_a set foo = 'bar' where eid = 1 and id in (1, 2) /* _stream vtocc_a (eid id ) (1 1 ) (1 2 ); */"),
         'commit',
         Case(sql='select foo from vtocc_a where id = 1',
              result=[('bar',)]),
         'begin',
         "update vtocc_a set foo='efgh' where id=1",
         "update vtocc_a set foo='fghi' where id=2",
         'commit']),

    MultiCase(
        'double in',
        ['begin',
         Case(sql="update /* pk */ vtocc_a set foo='bar' where eid in (1) and id in (1, 2)",
              rewritten=[
                  'select eid, id from vtocc_a where eid in (1) and id in (1, 2) limit 10001 for update',
                  "update /* pk */ vtocc_a set foo = 'bar' where eid = 1 and id = 1 /* _stream vtocc_a (eid id ) (1 1 ); */",
                  "update /* pk */ vtocc_a set foo = 'bar' where eid = 1 and id = 2 /* _stream vtocc_a (eid id ) (1 2 ); */",]),
         'commit',
         Case(sql='select foo from vtocc_a where id = 1',
              result=[('bar',)]),
         'begin',
         "update vtocc_a set foo='efgh' where id=1",
         "update vtocc_a set foo='fghi' where id=2",
         'commit']),

    MultiCase(
        'double in 2',
        ['begin',
         Case(sql="update /* pk */ vtocc_a set foo='bar' where eid in (1, 2) and id in (1, 2)",
              rewritten=[
                  'select eid, id from vtocc_a where eid in (1, 2) and id in (1, 2) limit 10001 for update',
                  "update /* pk */ vtocc_a set foo = 'bar' where eid = 1 and id = 1 /* _stream vtocc_a (eid id ) (1 1 ); */",
                  "update /* pk */ vtocc_a set foo = 'bar' where eid = 1 and id = 2 /* _stream vtocc_a (eid id ) (1 2 ); */"]),
         'commit',
         Case(sql='select foo from vtocc_a where id = 1',
              result=[('bar',)]),
         'begin',
         "update vtocc_a set foo='efgh' where id=1",
         "update vtocc_a set foo='fghi' where id=2",
         'commit']),

    MultiCase(
        'tuple in',
        ['begin',
         Case(sql="update /* pk */ vtocc_a set foo='bar' where (eid, id) in ((1, 1), (1, 2))",
              rewritten="update /* pk */ vtocc_a set foo = 'bar' where (eid, id) in ((1, 1), (1, 2)) /* _stream vtocc_a (eid id ) (1 1 ) (1 2 ); */"),
         'commit',
         Case(sql='select foo from vtocc_a where id = 1',
              result=[('bar',)]),
         'begin',
         "update vtocc_a set foo='efgh' where id=1",
         "update vtocc_a set foo='fghi' where id=2",
         'commit']),

  MultiCase(
      'pk change',
      ['begin',
       Case(sql="update vtocc_a set eid = 2 where eid = 1 and id = 1",
            rewritten="update vtocc_a set eid = 2 where eid = 1 and id = 1 /* _stream vtocc_a (eid id ) (1 1 ) (2 1 ); */"),
       'commit',
       Case(sql='select eid from vtocc_a where id = 1',
            result=[(2L,)]),
       'begin',
       "update vtocc_a set eid=1 where id=1",
       'commit']),

  MultiCase(
      'complex pk change',
      ['begin',
       Case(sql="update vtocc_a set eid = 1+1 where eid = 1 and id = 1",
            rewritten="update vtocc_a set eid = 1+1 where eid = 1 and id = 1"),
       'commit',
       Case(sql='select eid from vtocc_a where id = 1',
            result=[(2L,)]),
       'begin',
       "update vtocc_a set eid=1 where id=1",
       'commit']),

  MultiCase(
      'complex where',
      ['begin',
       Case(sql="update vtocc_a set eid = 1+1 where eid = 1 and id = 1+0",
            rewritten="update vtocc_a set eid = 1+1 where eid = 1 and id = 1+0"),
       'commit',
       Case(sql='select eid from vtocc_a where id = 1',
            result=[(2L,)]),
       'begin',
       "update vtocc_a set eid=1 where id=1",
       'commit']),

  MultiCase(
      'partial pk',
      ['begin',
       Case(sql="update /* pk */ vtocc_a set foo='bar' where id = 1",
            rewritten=[
                "select eid, id from vtocc_a where id = 1 limit 10001 for update",
                "update /* pk */ vtocc_a set foo = 'bar' where eid = 1 and id = 1 /* _stream vtocc_a (eid id ) (1 1 ); */"]),
       'commit',
       Case(sql='select foo from vtocc_a where id = 1',
            result=[('bar',)]),
       'begin',
       "update vtocc_a set foo='efgh' where id=1",
       'commit']),

  MultiCase(
      'limit',
      ['begin',
       Case(sql="update /* pk */ vtocc_a set foo='bar' where eid = 1 limit 1",
            rewritten=[
                "select eid, id from vtocc_a where eid = 1 limit 1 for update",
                "update /* pk */ vtocc_a set foo = 'bar' where eid = 1 and id = 1 /* _stream vtocc_a (eid id ) (1 1 ); */"]),
       'commit',
       Case(sql='select foo from vtocc_a where id = 1',
            result=[('bar',)]),
       'begin',
       "update vtocc_a set foo='efgh' where id=1",
       'commit']),

    MultiCase(
        'order by',
        ['begin',
         Case(sql="update /* pk */ vtocc_a set foo='bar' where eid = 1 order by id desc limit 1",
              rewritten=[
                  "select eid, id from vtocc_a where eid = 1 order by id desc limit 1 for update",
                  "update /* pk */ vtocc_a set foo = 'bar' where eid = 1 and id = 2 /* _stream vtocc_a (eid id ) (1 2 ); */"]),
         'commit',
         Case(sql='select foo from vtocc_a where id = 2',
              result=[('bar',)]),
         'begin',
         "update vtocc_a set foo='fghi' where id=2",
         'commit']),

  MultiCase(
      'missing where',
      ['begin',
       Case(sql="update vtocc_a set foo='bar'",
            rewritten=[
                "select eid, id from vtocc_a limit 10001 for update",
                "update vtocc_a set foo = 'bar' where eid = 1 and id = 1 /* _stream vtocc_a (eid id ) (1 1 ); */",
                "update vtocc_a set foo = 'bar' where eid = 1 and id = 2 /* _stream vtocc_a (eid id ) (1 2 ); */"]),
       'commit',
       Case(sql='select * from vtocc_a',
            result=[(1L, 1L, 'abcd', 'bar'), (1L, 2L, 'bcde', 'bar')]),
       'begin',
       "update vtocc_a set foo='efgh' where id=1",
       "update vtocc_a set foo='fghi' where id=2",
       'commit']),

  MultiCase(
      'no index',
      ['begin',
       "insert into vtocc_d(eid, id) values (1, 1)",
       Case(sql="update vtocc_d set id = 2 where eid = 1",
            rewritten="update vtocc_d set id = 2 where eid = 1"),
       'commit',
       Case(sql='select * from vtocc_d',
            result=[(1L, 2L)]),
       'begin',
       'delete from vtocc_d',
       'commit']),

  MultiCase(
      'delete',
      ['begin',
       "insert into vtocc_a(eid, id, name, foo) values (2, 1, '', '')",
       Case(sql="delete /* pk */ from vtocc_a where eid = 2 and id = 1",
            rewritten="delete /* pk */ from vtocc_a where eid = 2 and id = 1 /* _stream vtocc_a (eid id ) (2 1 ); */"),
       'commit',
       Case('select * from vtocc_a where eid=2',
            result=[])]),

  MultiCase(
      'single in',
      ['begin',
       "insert into vtocc_a(eid, id, name, foo) values (2, 1, '', '')",
       Case(sql="delete /* pk */ from vtocc_a where eid = 2 and id in (1, 2)",
            rewritten="delete /* pk */ from vtocc_a where eid = 2 and id in (1, 2) /* _stream vtocc_a (eid id ) (2 1 ) (2 2 ); */"),
       'commit',
       Case(sql='select * from vtocc_a where eid=2',
            result=[])]),

  MultiCase(
      'double in',
      ['begin',
       "insert into vtocc_a(eid, id, name, foo) values (2, 1, '', '')",
       Case(sql="delete /* pk */ from vtocc_a where eid in (2) and id in (1, 2)",
            rewritten=[
                'select eid, id from vtocc_a where eid in (2) and id in (1, 2) limit 10001 for update',
                'delete /* pk */ from vtocc_a where eid = 2 and id = 1 /* _stream vtocc_a (eid id ) (2 1 ); */',]),
       'commit',
       Case(sql='select * from vtocc_a where eid=2',
            result=[])]),

  MultiCase(
      'double in 2',
      ['begin',
       "insert into vtocc_a(eid, id, name, foo) values (2, 1, '', '')",
       Case(sql="delete /* pk */ from vtocc_a where eid in (2, 3) and id in (1, 2)",
            rewritten=[
                'select eid, id from vtocc_a where eid in (2, 3) and id in (1, 2) limit 10001 for update',
                'delete /* pk */ from vtocc_a where eid = 2 and id = 1 /* _stream vtocc_a (eid id ) (2 1 ); */']),
       'commit',
       Case(sql='select * from vtocc_a where eid=2',
            result=[])]),

  MultiCase(
      'tuple in',
      ['begin',
       "insert into vtocc_a(eid, id, name, foo) values (2, 1, '', '')",
       Case(sql="delete /* pk */ from vtocc_a where (eid, id) in ((2, 1), (3, 2))",
            rewritten="delete /* pk */ from vtocc_a where (eid, id) in ((2, 1), (3, 2)) /* _stream vtocc_a (eid id ) (2 1 ) (3 2 ); */"),
       'commit',
       Case(sql='select * from vtocc_a where eid=2',
            result=[])]),

  MultiCase(
      'complex where',
      ['begin',
       "insert into vtocc_a(eid, id, name, foo) values (2, 1, '', '')",
       Case(sql="delete from vtocc_a where eid = 1+1 and id = 1",
            rewritten=[
                'select eid, id from vtocc_a where eid = 1+1 and id = 1 limit 10001 for update',
                "delete from vtocc_a where eid = 2 and id = 1 /* _stream vtocc_a (eid id ) (2 1 ); */"]),
       'commit',
       Case(sql='select * from vtocc_a where eid=2',
            result=[])]),

  MultiCase(
      'partial pk',
      ['begin',
       "insert into vtocc_a(eid, id, name, foo) values (2, 1, '', '')",
       Case(sql="delete from vtocc_a where eid = 2",
            rewritten=[
                'select eid, id from vtocc_a where eid = 2 limit 10001 for update',
                "delete from vtocc_a where eid = 2 and id = 1 /* _stream vtocc_a (eid id ) (2 1 ); */"]),
       'commit',
       Case(sql='select * from vtocc_a where eid=2',
            result=[])]),

  MultiCase(
      'limit',
      ['begin',
      "insert into vtocc_a(eid, id, name, foo) values (2, 1, '', '')",
      Case(sql="delete from vtocc_a where eid = 2 limit 1",
           rewritten=[
               'select eid, id from vtocc_a where eid = 2 limit 1 for update',
               "delete from vtocc_a where eid = 2 and id = 1 /* _stream vtocc_a (eid id ) (2 1 ); */"]),
      'commit',
      Case(sql='select * from vtocc_a where eid=2',
           result=[])])
]