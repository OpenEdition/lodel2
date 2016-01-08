"""
    Test for LeType and childs
"""

import unittest
from unittest import TestCase
from unittest.mock import patch

import EditorialModel
import leapi
import DataSource.dummy
import leapi.test.utils

class LeTypeTestCase(TestCase):
    
    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leapi.test.utils.cleanup(cls.tmpdir)

    def test_init(self):
        """ testing the constructor """
        from dyncode import Publication, Numero, LeObject, LeType
        
        with self.assertRaises(NotImplementedError):
            LeType(42)

        badargs = [
            {'class_id':Numero._class_id + 1},
            {'type_id':Numero._type_id + 1},
        ]
        for badarg in badargs:
            with self.assertRaises(RuntimeError):
                Numero(42, **badarg)

        badargs = [
            ({'lodel_id':'foobar'}, TypeError),
            ({'lodel_id': 42, 'titre_mais_qui_existe_pas':'hello'}, leapi.lecrud.LeApiDataCheckError),
        ]
        for badarg, expect_e in badargs:
            with self.assertRaises(expect_e, msg="Invalid argument given %s"%badarg):
                Numero(**badarg)
    
    @patch('leapi.letype._LeType.populate')
    def test_datas(self, dsmock):
        """ Testing the datas @property method """
        from dyncode import Publication, Numero, LeObject
        num = Numero(42, titre = 'foofoo')
        self.assertEqual({'lodel_id' : 42, 'titre': 'foofoo'}, num.datas())
        num.all_datas
        dsmock.assert_called_once()

class LeTypeMockDsTestCase(TestCase):
    """ Tests that need to mock the datasource """

    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leapi.test.utils.cleanup(cls.tmpdir)

    @patch('DataSource.dummy.leapidatasource.DummyDatasource.select')
    def test_populate(self, dsmock):
        from dyncode import Publication, Numero, LeObject

        num = Numero(1, type_id = Numero._type_id)
        missing_fields = [f for f in Numero._fields if not (f in ['lodel_id', 'type_id'])]
        with self.assertRaises(leapi.lecrud.LeApiQueryError):
            num.populate()
            dsmock.assert_called_once_with(Numero, missing_fields, [('lodel_id','=',1)],[])

    @patch('DataSource.dummy.leapidatasource.DummyDatasource.update')
    @unittest.skip('must verify that populate is called')
    def test_update(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        
        datas = { 'titre' : 'foobar' }
        
        #Testing as instance method
        num = Numero(lodel_id = 1)
        num.update(datas)
        dsmock.assert_called_once_with(Numero, [('lodel_id','=',1)], [], **datas)
    
    @patch('DataSource.dummy.leapidatasource.DummyDatasource.delete')
    def test_delete(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        
        num = Numero(lodel_id = 1)
        num.delete()
        dsmock.assert_called_once_with(Numero, [('lodel_id','=',1)], [])

