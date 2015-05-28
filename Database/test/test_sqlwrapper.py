import os
import logging
import random

from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch, call
import unittest

import sqlalchemy
from Database.sqlwrapper import SqlWrapper

from django.conf import settings
from Database.sqlsettings import SQLSettings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

BADNAMES = ['',  "  \t  ", "bad--", "%", "*", "`", '"', "'", "\0", "hello`World", 'Hello"world', 'foo%', '*bar.*', '%%', "hello\0world", print, 42 ]

for c in ('*','%','`', "'", '"', "\\"):
    for _ in range(16):
        c = "\\"+c
        BADNAMES.append(c)
BADNAMES+=[chr(i) for i in list(range(0,0x09))+[0x0b, 0x0c]+list(range(0x0e, 0x01f))]

class SqlWrapperTests(TestCase):

    def setUp(self):
        #Overwriting database conf
        SQLSettings.DB_READ_CONNECTION_NAME = 'testdb'
        SQLSettings.DB_WRITE_CONNECTION_NAME = 'testdb'
        

        self.testdb = os.path.join('/tmp/', 'lodel2_testdb.sqlite3')

        settings.DATABASES['testdb'] = {
            'ENGINE': 'sqlite',
            'NAME': self.testdb,
        }
        #Disable logging but CRITICAL
        logging.basicConfig(level=logging.CRITICAL)
        pass

    def tearDown(self):
        try:
            os.unlink(self.testdb) #Removing the test database
        except FileNotFoundError: pass
    
    """ Testing standart instanciation of sqlwrapper """
    def test_init_sqlwrapper(self):
        sw = SqlWrapper()
        self.assertIsInstance(sw, SqlWrapper)
        sw2 = SqlWrapper()
        self.assertIsInstance(sw2, SqlWrapper)

    def test_get_engine(self):
        sw = SqlWrapper()
        engine = sw.get_engine(SQLSettings.DB_READ_CONNECTION_NAME)
        self.assertIsInstance(engine, sqlalchemy.engine.base.Engine)
    
    def test_get_engine_badargs(self):
        sw = SqlWrapper()
        with self.assertRaises(Exception):
            sw.get_engine(0)
        with self.assertRaises(Exception):
            sw.get_engine('')
        with self.assertRaises(Exception):
            sw.get_engine('           ')

    
    @patch.object(SqlWrapper, 'get_read_engine')
    def test_execute_queries(self, mock_read):
        queries = [ 'SELECT * FROM foo', 'SELECT * FROM bar', 'SELECT foo.id, bar.id FROM foo, bar WHERE foo.id = 42 AND bar.name = \'hello world !\'' ]

        mock_read.return_value = MagicMock()
        mock_engine = mock_read.return_value
        mock_engine.connect.return_value = MagicMock()
        mock_conn = mock_engine.connect.return_value
        sw = SqlWrapper()

        #One query execution
        sw.execute(queries[0], 'read')
        mock_conn.execute.assert_called_with(queries[0])
        mock_conn.reset_mock()

        #multiple queries execution
        sw.execute(queries, 'read')

        except_calls = [ call(q) for q in queries ]
        self.assertEqual(except_calls, mock_conn.execute.mock_calls)

    @patch.object(sqlalchemy.ForeignKeyConstraint, '__init__')
    def test_create_fk_constraint_mock(self, mock_fk):
        mock_fk.return_value = None

        sw = SqlWrapper()
        sw.create_foreign_key_constraint_object('foo','bar', 'foobar')
        mock_fk.asser_called_with(['foo'], ['bar'], 'foobar')

    def test_create_fk_constraint(self):
        sw = SqlWrapper()
        fk = sw.create_foreign_key_constraint_object('foo', 'bar', 'foobar')
        self.assertIsInstance(fk, sqlalchemy.ForeignKeyConstraint)
        
    @unittest.skip('Dev') #TODO remove it
    def test_create_fk_constraint_badargs(self):
        sw = SqlWrapper()

        
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object(['foo', 'bar'], 'foofoo', 'babar')
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object('bar', 2, 'babar')
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object(None, 'foo', 'bar')
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object('bar', None, 'babar')
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object(None, None, 'babar')
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object(print, 'foo', 'babar')
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object('foo', print, 'babar')
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object('foo', 'bar', print)
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object('bar', 'foo', 42)
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object('bar', 'foo', '   ')
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object(" \t  ", 'foo')
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object('bar', 'foo', "  \t ")

        foocol = sqlalchemy.Column('foo',sqlalchemy.INTEGER)

        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object(foocol, foocol)
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object(foocol, 'bar')
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object('foo', foocol)
        with self.assertRaises(Exception):
            sw.create_foreign_key_constraint_object('foo', 'bar', foocol)
    
    @patch.object(sqlalchemy.Column, '__init__')
    def test_create_column(self, mockcol):
        mockcol.return_value = None
        sw = SqlWrapper()
        foo = sw.create_column_object('foo', 'INTEGER')
        mockcol.assert_called_once_with('foo', sqlalchemy.INTEGER)
        mockcol.reset_mock()

        foo = sw.create_column_object('foo', 'VARCHAR(50)')
        self.assertEqual(mockcol.call_args[0][0], 'foo')
        self.assertIsInstance(mockcol.call_args[0][1], sqlalchemy.VARCHAR)
        self.assertEqual(mockcol.call_args[0][1].length, 50)
        mockcol.reset_mock()

        foo = sw.create_column_object('foo', 'TEXT')
        mockcol.assert_called_once_with('foo', sqlalchemy.TEXT)
        mockcol.reset_mock()

        foo = sw.create_column_object('foo', 'DATE')
        mockcol.assert_called_once_with('foo', sqlalchemy.DATE)
        mockcol.reset_mock()

        foo = sw.create_column_object('foo', 'BOOLEAN')
        mockcol.assert_called_once_with('foo', sqlalchemy.BOOLEAN)
        mockcol.reset_mock()
 
        xtrmlongname = ''
        for _ in range(200):
            xtrmlongname += 'veryvery'
        xtrmlongname += 'longname'

        foo = sw.create_column_object(xtrmlongname, 'TEXT')
        mockcol.assert_called_once_with(xtrmlongname, sqlalchemy.TEXT)
        mockcol.reset_mock()

    def test_create_column_extra_fk(self):
        sw = SqlWrapper()

        extra = { 'foreignkey': 'bar' }
        rescol = sw.create_column_object('foo', 'INTEGER', extra)
        self.assertIsInstance(rescol, sqlalchemy.Column)
        fk = rescol.foreign_keys.pop()
        self.assertIsInstance(fk, sqlalchemy.ForeignKey)
        self.assertEqual(fk._colspec, 'bar')

    def test_create_column_extra_default(self):
        sw = SqlWrapper()


        extra = { 'default': None, 'nullable': True }
        rescol = sw.create_column_object('foo', 'INTEGER', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, None)

        extra = { 'default': "NULL", 'nullable': True }
        rescol = sw.create_column_object('foo', 'INTEGER', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, "NULL")

        extra = { 'default': 'null', 'nullable': True }
        rescol = sw.create_column_object('foo', 'INTEGER', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, 'null')

        extra = { 'default': 42 }
        rescol = sw.create_column_object('foo', 'INTEGER', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, 42)

        extra = { 'default': 'foobardefault' }
        rescol = sw.create_column_object('foo', 'VARCHAR(50)', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, 'foobardefault')

        extra = { 'default': 'foodefault' }
        rescol = sw.create_column_object('foo', 'TEXT', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, 'foodefault')

        extra = { 'default': True }
        rescol = sw.create_column_object('foo', 'BOOLEAN', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, True)

        extra = { 'default': False }
        rescol = sw.create_column_object('foo', 'BOOLEAN', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, False)

        extra = { 'default': "true" }
        rescol = sw.create_column_object('foo', 'BOOLEAN', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, "true")

        extra = { 'default': 0 }
        rescol = sw.create_column_object('foo', 'BOOLEAN', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, 0)

        extra = { 'default': 1 }
        rescol = sw.create_column_object('foo', 'BOOLEAN', extra)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, 1)


    def test_create_column_extra_pknull(self):
        sw = SqlWrapper()

        for b in (True,False):
            extra = { 'primarykey': b }
            rescol = sw.create_column_object('foo', 'INTEGER', extra)
            self.assertIsInstance(rescol, sqlalchemy.Column)
            self.assertEqual(rescol.primary_key, b)

            extra = { 'nullable': b }
            rescol = sw.create_column_object('foo', 'INTEGER', extra)
            self.assertIsInstance(rescol, sqlalchemy.Column)
            self.assertEqual(rescol.nullable, b)

            extra = { 'primarykey' : b, 'nullable': not b }
            rescol = sw.create_column_object('foo', 'INTEGER', extra)
            self.assertIsInstance(rescol, sqlalchemy.Column)
            self.assertEqual(rescol.primary_key, b)
            self.assertEqual(rescol.nullable, not b)

            extra = { 'primarykey' : b, 'nullable': b }
            rescol = sw.create_column_object('foo', 'INTEGER', extra)
            self.assertIsInstance(rescol, sqlalchemy.Column)
            self.assertEqual(rescol.primary_key, b)
            self.assertEqual(rescol.nullable, b)



    def test_create_column_extra_all(self):
        sw = SqlWrapper()

        extra = { 'primarykey': False, 'nullable': False, 'default':42, 'foreignkey': 'foobar'}
        rescol = sw.create_column_object('foo', 'INTEGER', extra)
        self.assertIsInstance(rescol, sqlalchemy.Column)
        self.assertEqual(rescol.primary_key, False)
        self.assertEqual(rescol.nullable, False)
        self.assertIsInstance(rescol.default, sqlalchemy.ColumnDefault)
        self.assertEqual(rescol.default.arg, 42)
        fk = rescol.foreign_keys.pop()
        self.assertIsInstance(fk, sqlalchemy.ForeignKey)
        self.assertEqual(fk._colspec, 'foobar')

    @unittest.skip('Dev') #TODO remove it
    def test_create_column_badargs(self):
        sw = SqlWrapper()
        
        cc = sw.create_column_object
        ain = self.assertIsNone
        
        for bname in BADNAMES:
            ain(cc(bname, 'INTEGER'))

        ain(cc('c', 'INNNTEGER'))
        ain(cc(" \t\t  ", 'TEXT'))
        ain(cc('c', '             '))
        ain(cc('c', 'VARCHAR(foo)'))
        ain(cc('supercol', 'SUPERNOTTYPEDVARCHARSTR'))

        ain(cc('c', None))
        ain(cc(None, None))

    @unittest.skip('Dev') #TODO remove it
    def test_create_column_badextra(self):
        sw = SqlWrapper()

        cc = sw.create_column_object
        ain = self.assertIsNone
        
        #Put junk in extra datas
        for xtra_name in [ 'primarykey', 'nullable', 'foreignkey' ]:
            for junk in [ print, sqlalchemy, SqlWrapper, '   ' ]+BADNAMES:
                ain(cc('c', 'TEXT', { xtra_name: junk }))

        for junk in [True, False, 52, '   ']+BADNAMES:
            ain(cc('c', 'TEXT', { 'foreignkey': junk }))

        for xtra_name in ('primarykey', 'nullalble'):
            for junk in [4096, 'HELLO WORLD !', '   ']+BADNAMES:
                ain(cc('c', 'TEXT', { xtra_name, junk } ))

    @patch.object(sqlalchemy.Table, '__init__')
    def test_create_table(self, mock_table):
        #TODO check constraints
        """ Create tables and check that the names are ok """
        mock_table.return_value = None
        sw = SqlWrapper()
        
        cols = [
            { 'name': 'supercol', 'type': 'INTEGER', 'extra': { 'nullable': True } },
            { 'name': 'superpk', 'type': 'INTEGER', 'extra': { 'primarykey': True} },
            { 'name': 'col2', 'type': 'TEXT' }
        ]
        
        for table_name in ['supertable', 'besttableever', 'foo-table']:

            params = { 'name': table_name, 'columns': cols, 'constraints':dict() }

            self.assertTrue(sw.create_table(params))
            self.assertEqual(mock_table.call_args[0][0], table_name)
        pass
    
    @patch.object(sqlalchemy.Table, 'append_column')
    def test_create_table_col(self, mock_append):
        #TODO check constraints
        """ Create a table and check that the columns are OK """
        sw = SqlWrapper()
        
        table_name = 'supertablecol'

        cols = [
            { 'name': 'supercol', 'type': 'INTEGER', 'extra': { 'nullable': True } },
            { 'name': 'superpk', 'type': 'INTEGER', 'extra': { 'primarykey': True} },
            { 'name': 'col2', 'type': 'TEXT' }
        ]

        except_coltype = [ sqlalchemy.INTEGER, sqlalchemy.INTEGER, sqlalchemy.TEXT ]

        params = { 'name': table_name, 'columns': cols, 'constraints':dict() }
    
        sw.create_table(params) #This call return false because of the mock on append_column
        
        self.assertEqual(len(mock_append.mock_calls), len(cols))

        for n,c in enumerate(mock_append.mock_calls):
            self.assertEqual(c[1][0].name, cols[n]['name'])
            self.assertIsInstance(c[1][0].type, except_coltype[n])
        pass
    
    def test_create_table_recreate(self):
        #TODO check constraints
        """ Try to create the same table 2 times (except a False return the second time) """
        sw = SqlWrapper()

        params = { 'name': 'redondant', 'columns': [{'name':'foocol', 'type': 'INTEGER'}]}

        self.assertTrue(sw.create_table(params))

        params['columns'] = [{'name':'barcol', 'type': 'INTEGER'}]

        self.assertFalse(sw.create_table(params))

    @unittest.skip('dev') #TODO remove it
    def test_create_table_badargs(self):
        sw = SqlWrapper()

        af = self.assertFalse
        ct = sw.create_table

        foocol = {'name': 'foocol', 'type': 'INTEGER'}

        p = {'name': 'foo'}
        af(ct(p)) #no columns
        for bname in BADNAMES: #bad column name
            p['columns'] = bname
            af(ct(p))
        p['columns']=[]; af(ct(p)) #empty columns TODO Or return True is normal ???


        p = {'columns':[foocol]}
        af(ct(p)) #no name
        for bname in BADNAMES:
            p['name'] = bname
            af(ct(p))
        pass

    
    def create_test_table(self, sw):
        """ Create a table for test purpose """
        table_name = 'testtable'
        cols = [
            { 'name': 'pk', 'type': 'INTEGER', 'extra': {'primarykey': True} },
            { 'name': 'testtxt', 'type': 'TEXT', 'extra': {'nullable': True, 'default': 'hello'} },
            { 'name': 'testchr', 'type': 'VARCHAR(50)', 'extra': {'nullable': True, 'default': 'hello world'} },
        ]
        
        sw.create_table( { 'name': table_name, 'columns': cols} )
        pass
    
    def test_get_table(self):
        """ Try to get the testtable (check the name and type of return) """
        sw = SqlWrapper()

        self.create_test_table(sw)

        rt = sw.get_table('testtable')
        self.assertIsInstance(rt, sqlalchemy.Table)
        self.assertEqual(rt.name, 'testtable')

        rt = sw.get_table('testtable', 'write')
        self.assertIsInstance(rt, sqlalchemy.Table)
        self.assertEqual(rt.name, 'testtable')

        rt = sw.get_table('testtable', 'read')
        self.assertIsInstance(rt, sqlalchemy.Table)
        self.assertEqual(rt.name, 'testtable')
        pass

    @unittest.skip('dev') #TODO remove skip
    def test_get_table_badargs(self):
        sw = SqlWrapper()

        self.create_test_table(sw)

        for badname in BADNAMES:
            with self.assertRaises((sqlalchemy.exc.NoSuchTableError, Exception)):
                sw.get_table(badname)

        with self.assertRaises(sqlalchemy.exc.NoSuchTableError):
            sw.get_table('FOOBAR')
        with self.assertRaises(Exception):
            sw.get_table(print)
        with self.assertRaises(Exception):
            sw.get_table(1)

        #bad action types
        with self.assertRaises(Exception):
            sw.get_table('testtable', print)
        with self.assertRaises(Exception):
            sw.get_table('testtable', 'foobar')
        with self.assertRaises(Exception):
            sw.get_table('testtable', 42)
        pass

    def test_drop_table(self):
        sw = SqlWrapper()
        
        self.create_test_table(sw)

        self.assertTrue(sw.drop_table('testtable'))
        self.assertFalse(sw.drop_table('testtable'))
        self.assertFalse(sw.drop_table('nonexisting'))
        pass

    def test_drop_table_badargs(self):
        sw = SqlWrapper()

        self.create_test_table(sw)

        af = self.assertFalse

        for bname in BADNAMES:
            self.assertFalse(sw.drop_table(bname))

    def test_create_get_drop_table(self):
        sw = SqlWrapper()
        
        funkynames = ('standart', "wow-nice", "-really-", "test_test-test", "_test", "test_", "test42", "foobar_123", "foobar-123", "foofoo--babar")
        types = ['INTEGER', 'VARCHAR(5)', 'VARCHAR(128)', 'TEXT', 'BOOLEAN']
        params = dict()

        cols = []
        for i,name in enumerate(funkynames):
            cols.append({'name':name, 'type':types[i%len(types)]})
        params['columns'] = cols


        for name in random.sample(funkynames, len(funkynames)):
            params['name'] = name
            self.assertTrue(sw.create_table(params))

        for name in random.sample(funkynames, len(funkynames)):
            rt = sw.get_table(name)
            self.assertIsInstance(rt, sqlalchemy.Table)#do we get a table ?
            self.assertEqual(rt.name, name)

        for name in random.sample(funkynames, len(funkynames)):
            self.assertTrue(sw.drop_table(name))
        pass
        

