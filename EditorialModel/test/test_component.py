import os
import logging

#from django.test import TestCase
from django.conf import settings

from unittest import TestCase
import unittest

from EditorialModel.components import EmComponent, EmComponentNotExistError

from Database.sqlsetup import SQLSetup
from Database.sqlwrapper import SqlWrapper
from Database import sqlutils
import sqlalchemy as sqla

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")


#A dummy EmComponent child class use to make tests
class EmTestComp(EmComponent):
    table = 'ttest'
    def __init__(self, ion):
        super(EmTestComp, self).__init__(ion)

class ComponentTestCase(TestCase):

    # ############# # 
    #  TESTS SETUP  #
    # ############# #
    @classmethod
    def setUpClass(cls):
        #Overwritting db confs to make tests
        settings.LODEL2SQLWRAPPER = {
            'default': {
                'ENGINE': 'sqlite',
                'NAME': '/tmp/testdb.sqlite'
            }
        }
        
        #Disable logging but CRITICAL
        logging.basicConfig(level=logging.CRITICAL)

        #testDB setup
        #   TODO May be slow
        sqls = SQLSetup()
        tables = sqls.get_schema()
        ttest = {   'name':'ttest',
                    'columns':  [
                        {"name":"uid",          "type":"INTEGER", "extra":{"foreignkey":"uids.uid", "nullable":False, "primarykey":True}},
                        {"name":"name",         "type":"VARCHAR(50)", "extra":{"nullable":False, "unique":True}},
                        {"name":"string",       "type":"TEXT"},
                        {"name":"help",         "type":"TEXT"},
                        {"name":"rank",         "type":"INTEGER"},
                        {"name":"date_update",  "type":"DATE"},
                        {"name":"date_create",  "type":"DATE"}
                    ]
                }
        tables.append(ttest)

        
        cls.db = SqlWrapper(read_db='default', write_db = 'default')
        cls.tables = tables

    @property
    def db(self):
        return self.__class__.db
    @property
    def tables(self):
        return self.__class__.tables

    def setUp(self):
        # Db RAZ
        self.db.dropAll()
        # Db schema creation
        self.db.createAllFromConf(self.tables);
        self.dber = self.db.r_engine
        self.dbew = self.db.w_engine
        
        # Test Em creation
        conn = self.dber.connect()
        test_table = sqla.Table(EmTestComp.table, sqlutils.meta(self.dber))
        uids_table = sqla.Table('uids', sqlutils.meta(self.dber))
        tuid = [ 1, 2, 3 , 42, 84 , 1025 ]

        #Creating uid for the EmTestComp
        for uid in tuid:
            req = uids_table.insert(values={'uid':uid, 'table': EmTestComp.table })
            conn.execute(req)

        self.test_values = [
            { 'uid': tuid[0], 'name': 'test', 'string': 'testcomp', 'help': 'help test', 'rank': 0},
            { 'uid': tuid[1], 'name': 'test-em_comp', 'string': 'Super test comp', 'help': '', 'rank': 1},
            { 'uid': tuid[2], 'name': 'test2', 'string': '', 'help': '', 'rank': 3},
            { 'uid': tuid[3], 'name': 'foo', 'string': 'bar', 'help': 'foobar', 'rank': 1337},
            { 'uid': tuid[4], 'name': '123', 'string': '456', 'help': '4242', 'rank': 42},
            { 'uid': tuid[5], 'name': 'name', 'string': 'string', 'help': 'help', 'rank': 12},
        ]

        req = test_table.insert(values=self.test_values)
        conn.execute(req)
        conn.close()
        pass
    
    # ############# #
    #  TESTS BEGIN  #
    # ############# #

    #
    #   EmComponent.newUid
    #
    def test_newuid(self):
        """ Test valid calls for newUid method """
        for _ in range(10):
            nuid = EmTestComp.newUid()
        
            conn = self.dber.connect()
            tuid = sqla.Table('uids', sqlutils.meta(self.dber))
            req = sqla.select([tuid]).where(tuid.c.uid == nuid)
            rep = conn.execute(req)
            res = rep.fetchall()
        
            self.assertEqual(len(res), 1)
            res = res[0]
            self.assertEqual(res.uid, nuid)
            self.assertEqual(res.table, EmTestComp.table)
        pass

    @unittest.skip("Enable me!") #TODO stop skipping it
    def test_newuid_abstract(self):
        """ Test not valit call for newUid method """
        with self.assertRaises(NotImplementedError):
            EmComponent.newUid()
        pass
    #
    #   EmComponent.__init__
    #
    @unittest.skip("Enable me!") #TODO stop skipping it
    def test_component_abstract_init(self):
        """ Test not valid call (from EmComponent) of __init__ """
        with self.assertRaises(NotImplementedError):
            test_comp = EmComponent(2)
        with self.assertRaises(NotImplementedError):
            test_comp = EmComponent('name')
        pass


    def test_component_init_not_exist(self):
        """ Test __init__ with non existing objects """
        with self.assertRaises(EmComponentNotExistError):
            test_comp = EmTestComp('not_exist')

        # TODO this assertion depends of the EmComponent behavior when instanciate with an ID
        #with self.assertRaises(EmComponentNotExistError):
        #    test_comp = EmTestComp(4096)

        pass

    def test_component_init_uid(self):
        """ Test __init__ with numerical ID """
        for val in self.test_values:
            test_comp = EmTestComp(val['uid'])
            self.assertIsInstance(test_comp, EmTestComp)
            self.assertEqual(test_comp.id, val['uid'])
        pass

    def test_component_init_name(self):
        """ Test __init__ with names """
        for val in self.test_values:
            test_comp = EmTestComp(val['name'])
            self.assertIsInstance(test_comp, EmTestComp)
            for vname in val:
                if vname == 'uid':
                    prop = 'id'
                else:
                    prop = vname
                self.assertEqual(test_comp.__get_attr__(prop), val[vname])
        pass
        
        
