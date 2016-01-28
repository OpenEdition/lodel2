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
from leapi.lecrud import _LeCrud

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

    def test_fieldlist(self):
        """ Test fieldlist method """
        from dyncode import Numero, Rubrique, Article, Personne, LeObject

        letypes = [Numero, Rubrique, Article, Personne]

        for letype in letypes:
            self.assertEqual(
                letype.fieldlist(complete=False),
                letype._fields
            )
            self.assertEquals(
                sorted(letype.fieldlist(complete = True)),
                sorted(list(set(letype._fields + LeObject.fieldlist())))
            )
            for fname in letype.fieldlist(complete = False):
                self.assertIn(fname, letype._leclass.fieldlist(False))
                ftype = letype.fieldtypes()[fname]
                self.assertNotIn(fname, LeObject.fieldlist())

    def test_fieldtypes(self):
        """ Test fieldtypes() method """
        from dyncode import Numero, Rubrique, Article, Personne, LeObject

        letypes = [Numero, Rubrique, Article, Personne]

        for letype in letypes:
            for complete in [True, False]:
                self.assertEquals(
                    sorted(letype.fieldlist(complete = complete)),
                    sorted(list(letype.fieldtypes(complete = complete).keys()))
                )



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
    def test_update(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        
        datas = { 'titre' : 'foobar' }
        
        #Testing as instance method
        num = Numero(lodel_id = 1)
        with patch.object(_LeCrud, 'populate', return_value=None) as mock_populate:
            num.update(datas)
            mock_populate.assert_called_once_with()
            dsmock.assert_called_once_with(Numero, num.uidget(), **datas)
    
    @patch('DataSource.dummy.leapidatasource.DummyDatasource.delete')
    def test_delete(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        
        num = Numero(lodel_id = 1)
        num.delete()
        dsmock.assert_called_once_with(Numero, 1)

