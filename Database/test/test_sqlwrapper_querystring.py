import os
import logging
import random

from unittest import TestCase
import unittest

from Database.sqlwrapper import SqlWrapper

from django.conf import settings
from Database.sqlsettings import SQLSettings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

#Bad strings for injection tests
INJECTIONS = [ 'foo UNION SELECT 1,2,3,4--', "foo' UNION SELECT 1,2,3--", 'foo" UNION SELECT 1,2,3--', 'foo` UNION SELECT 1,2,3,4--', '--', 'foo`; SELECT 1,2,3', 'foo"; SELECT 1,2,3', "foo'; SELECT 1,2,3", "; SELECT 1,2,3" ]
NAMEINJECT = INJECTIONS + [ '%', '*', "\0", "\b\b\b\b\b\b\b\b\b" ]

#Valid SQL types
VTYPES = [ 'integer', 'varchar(1)', 'varchar(50)', 'text', 'boolean' ]

class SqlWrapperQueryStrTests(TestCase):
    
    def setUp(self):
        #creating a test table
        sw = SqlWrapper()
        self.ttn = 'testtable'
        self.cols = [
            { 'name': 'pk', 'type': 'INTEGER', 'extra': {'primarykey': True} },
            { 'name': 'testtxt', 'type': 'TEXT', 'extra': {'nullable': True, 'default': 'hello'} },
            { 'name': 'testchr', 'type': 'VARCHAR(50)', 'extra': {'nullable': True, 'default': 'hello world'} },
            { 'name': 'testbool', 'type': 'BOOLEAN', 'extra': {'nullable':False, 'default': False}},
        ]
        
        sw.create_table( { 'name': self.ttn, 'columns': self.cols} )


        #Disable logging but CRITICAL
        logging.basicConfig(level=logging.CRITICAL)
        pass

    def tearDown(self):
        sw = SqlWrapper()
        sw.drop_table(self.ttn)

    @unittest.skip('dev') #TODO remove skip
    def test_get_querystring(self):
        sw = SqlWrapper()

        actions = [ 'add_column', 'alter_column', 'drop_column' ]
        dialects = [ 'default', 'mysql', 'postgresql' ]

        for action in actions:
            for dialect in dialects:
                r = sw.get_querystring(action, dialect)
                self.assertIsInstance(r, str)

    @unittest.skip('dev') #TODO remove skip
    def test_get_querystring_badargs(self):
        sw = SqlWrapper()
        
        actions = [ 1, -1, print, [], 'foo']
        dialects = actions
        for action in actions:
            for dialect in dialects:
                with self.assertRaises(ValueError):
                    r = sw.get_querystring(action, dialect)
    
    @unittest.skip('dev') #TODO remove skip
    def test_add_column(self):
        sw = SqlWrapper()

        colnames = [ 'taddcol1', 'test-add-col', 'test_add_col', '-test', '_add', '__col__' ]

        for i, name in enumerate(colnames):
            col = { 'name': name, 'type': VTYPES[i%len(VTYPES)] }
            self.assertTrue(sw.add_column(self.ttn, col))
        pass

    @unittest.skip('dev') #TODO remove skip
    def test_add_column_badargs(self):
        sw = SqlWrapper()

        coolname = 'cool'
        i=0
        self.assertFalse(sw.add_column(self.ttn, {'type': 'INTEGER'}))
        self.assertFalse(sw.add_column(self.ttn, {'name': 'foo'}))
        self.assertFalse(sw.add_column(self.ttn, dict()))
        self.assertFalse(sw.add_column(self.ttn, print))
        self.assertFalse(sw.add_column(self.ttn, ['foo', 'integer']))
        self.assertFalse(sw.add_column(self.ttn, None))
        self.assertFalse(sw.add_column(self.ttn, 42))
        self.assertFalse(sw.add_column(1, {'name':'foo', 'type':'integer'}))
        self.assertFalse(sw.add_column(print, {'name':'foo', 'type':'integer'}))
        self.assertFalse(sw.add_column([], {'name':'foo', 'type':'integer'}))
        self.assertFalse(sw.add_column(dict(), {'name':'foo', 'type':'integer'}))
        for badname in NAMEINJECT:
            self.assertFalse(sw.add_column(self.ttn, {'name':badname, 'type':'INTEGER'}))
            self.assertFalse(sw.add_column(self.ttn, {'name':coolname+str(i), 'type':badname}))
            self.assertFalse(sw.add_column(badname, {'name':coolname+str(i), 'type':'INTEGER'}))
            i+=1
        
    @unittest.skip('dev') #TODO remove skip
    def test_alter_column(self):
        sw = SqlWrapper()

        colnames = ['talter', 'talter1', 'test_alter', 'test-alter-col', '-test_alter', '__test_alter__']
        for i,name in enumerate(random.sample(colnames, len(colnames))):
            col = { 'name': name, 'type': VTYPES[i%len(VTYPES)] }
            self.assertTrue(sw.add_column( self.ttn, col))

        for i,name in enumerate(random.sample(colnames, len(colnames))):
            col = {'name': name, 'type': VTYPES[i%len(VTYPES)]}
            self.assertTrue(self.ttn, col)
        pass

    @unittest.skip('dev') #TODO remove skip
    def test_alter_column_badargs(self):
        sw = SqlWrapper()

        colnames = ['tabad', 'tabad1']

        for i,name in enumerate(colnames):
            col = { 'name': name, 'type': VTYPES[i%len(VTYPES)] }
            self.assertTrue(sw.add_column(self.ttn, col))

        for i,badname in enumerate(NAMEINJECT):
            col = { 'name': badname, 'type': VTYPES[i%len(VTYPES)] }
            self.assertFalse(sw.alter_column(self.ttn, col))

            col = { 'name': colnames[i%len(colnames)], 'type': badname}
            self.assertFalse(sw.alter_column(self.ttn, col))

            col = { 'name': badname, 'type': NAMEINJECT[random.randint(0,len(NAMEINJECT))]}
            self.assertFalse(sw.alter_column(self.ttn, col))

            col = { 'name': colnames[i%len(colnames)], 'type': VTYPES[i%len(VTYPES)] }
            self.assertFalse(sw.alter_column(badname, col))

    def test_insert(self):
        sw = SqlWrapper()

        records = [
            {   'pk': 0,
                'testchr': 'Hello world !',
                'testtext': 'Wow ! Super text... I\'m amazed',
                'testbool': False
            },
            {   'pk': 1,
                'testchr': 'Hello"world...--',
                'testtext': 'Another wonderfull text. But this time with spécials chars@;,:--*/+\'{}]{[|~&ù^$*µ$£ê;<ç>\/*-+',
                'testbool': True
            },
            {   'pk': 2 }, #default values for others
            {   'pk': '3',
                'testchr': None,
                'testtext': None,
                'testbool': 'true'
            },
            {   'pk': 4,
                'testchr': '',
                'testtext': '',
                'testbool': 'false'
            },
            {   'pk': 5,
                'testbool': 0
            },
            {   'pk': 6,
                'testbool': 1
            },
            {   'pk':1024,
                'testbool': False
            },
        ]
                
