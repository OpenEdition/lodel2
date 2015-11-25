"""
    Test for LeType and childs
"""

import unittest
from unittest import TestCase
from unittest.mock import patch

import EditorialModel
import leapi
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
        from dyncode import Publication, Numero, LeObject
        
        with self.assertRaises(NotImplementedError):
            leapi.letype.LeType(42)

        badargs = [
            {'class_id':Numero._class_id + 1},
            {'type_id':Numero._type_id + 1},
        ]
        for badarg in badargs:
            with self.assertRaises(RuntimeError):
                Numero(42, **badarg)

        badargs = [
            ({'lodel_id':'foobar'}, TypeError),
            ({'lodel_id': 42, 'titre_mais_qui_existe_pas':'hello'}, AttributeError),
        ]
        for badarg, expect_e in badargs:
            with self.assertRaises(expect_e, msg="Invalid argument given %s"%badarg):
                Numero(**badarg)
    
    ## @todo when we will have a field in a type that has a check_function try to make check_datas_or_raise raise with invalid value
    def test_check_datas(self):
        """ testing the check_datas* methods """
        from dyncode import Publication, Numero, LeObject

        datas = { 'titre':'foobar' }
        Numero.check_datas(datas, False)
        Numero.check_datas(datas, True)
        with self.assertRaises(leapi.leobject.LeObjectError):
            Numero.check_datas_or_raise({}, True)

    @patch('leapi.letype.LeType.populate')
    def test_datas(self, dsmock):
        """ Testing the datas @property method """
        from dyncode import Publication, Numero, LeObject
        num = Numero(42, titre = 'foofoo')
        self.assertEqual({'lodel_id' : 42, 'titre': 'foofoo'}, num.datas)
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

    @unittest.skip('Dummy datasource doesn\'t fit anymore')
    @patch('leapi.datasources.dummy.DummyDatasource.get')
    def test_populate(self, dsmock):
        from dyncode import Publication, Numero, LeObject

        num = Numero(1, type_id = Numero._type_id)
        missing_fields = [f for f in Numero._fields if not (f in ['lodel_id', 'type_id'])]
        num.populate()
        dsmock.assert_called_once_with(Publication, Numero, missing_fields, [('lodel_id','=','1')],[])

    @unittest.skip("Waiting for reimplementation in LeCrud")
    @patch('leapi.datasources.dummy.DummyDatasource.update')
    def test_update(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        
        datas = { 'titre' : 'foobar', 'string': 'wow' }

        Numero.update(['lodel_id = 1'], datas)
        dsmock.assert_called_once_with(Numero, Publication, [('lodel_id','=','1')], [], datas)
    
    @unittest.skip("Waiting for reimplementation in LeCrud")
    @patch('leapi.datasources.dummy.DummyDatasource.delete')
    def test_delete(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        
        Numero.delete(['lodel_id = 1'])
        dsmock.assert_called_once_with(Numero, Publication, [('lodel_id','=','1')], [])

    @unittest.skip("Waiting for reimplementation in LeCrud")
    @patch('leapi.datasources.dummy.DummyDatasource.update')
    def test_db_update(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        
        num = Numero(1, type_id = Numero._type_id, class_id = Numero._class_id, titre = 'Hello world !')
        num.db_update()
        dsmock.assert_called_once_with(Numero, Publication, [('lodel_id','=','1')], [], num.datas)

    @unittest.skip("Waiting for reimplementation in LeCrud")
    @patch('leapi.datasources.dummy.DummyDatasource.delete')
    def test_db_delete(self, dsmock):
        from dyncode import Publication, Numero, LeObject

        num = Numero(1, type_id = Numero._type_id, class_id = Numero._class_id, titre = 'Hello world !')
        num.db_delete()
        dsmock.assert_called_once_with(Numero, Publication, [('lodel_id','=','1')], [])

