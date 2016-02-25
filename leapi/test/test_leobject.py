"""
    Tests for _LeObject and LeObject
"""

import copy

import unittest
from unittest import TestCase
from unittest.mock import patch

import EditorialModel
import DataSource.dummy
import leapi
import leapi.test.utils
from leapi.leobject import _LeObject
from leapi.lecrud import _LeCrud

## Testing methods that need the generated code
class LeObjectTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()

    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leapi.test.utils.cleanup(cls.tmpdir)

    def test_uid2leobj(self):
        """ Testing _Leobject.uid2leobj() """
        import dyncode
        from dyncode import LeType, LeClass
        for i in dyncode.LeObject._me_uid.keys():
            cls = dyncode.LeObject.uid2leobj(i)
            if LeType in cls.__bases__:
                self.assertEqual(i, cls._type_id)
            elif LeClass in cls.__bases__:
                self.assertEqual(i, cls._class_id)
            else:
                self.fail("Bad value returned : '%s'"%cls)
        i=10
        while i in dyncode.LeObject._me_uid.keys():
            i+=1
        with self.assertRaises(KeyError):
            dyncode.LeObject.uid2leobj(i)
    
class LeObjectMockDatasourceTestCase(TestCase):
    """ Testing _LeObject using a mock on the datasource """

    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leapi.test.utils.cleanup(cls.tmpdir)
    
    @patch('DataSource.dummy.leapidatasource.LeapiDataSource.insert')
    def test_insert(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        ndatas = [
            {'titre' : 'FooBar'},
            {'titre':'hello'},
            {'titre':'world'},
        ]
        for ndats in ndatas:
            # Adding values for internal fields
            expt_dats = copy.copy(ndats)
            expt_dats['string'] = None
            expt_dats['class_id'] = Publication._class_id
            expt_dats['type_id'] = Numero._type_id

            Publication.insert(ndats, classname='Numero')
            dsmock.assert_called_once_with(Numero, **expt_dats)
            dsmock.reset_mock()

            LeObject.insert(ndats, classname = 'Numero')
            dsmock.assert_called_once_with(Numero, **expt_dats)
            dsmock.reset_mock()

    @patch('DataSource.dummy.leapidatasource.LeapiDataSource.update')
    def test_update(self, dsmock):
        from dyncode import Publication, Numero, LeObject, Personne, Article, RelTextesPersonneAuteur

        args = [
            (Article(42), {'titre': 'foobar'}),
            (Personne(51), {'nom': 'foobar'}),
            (RelTextesPersonneAuteur(1337), {'adresse': 'foobar'}),
        ]

        for instance, datas in args:
            with patch.object(_LeCrud, 'populate', return_value=None) as mock_populate:
                instance.update(datas)
                mock_populate.assert_called_once_with()
                dsmock.assert_called_once_with(instance.__class__, instance.uidget(), **datas)
                dsmock.reset_mock()
    
    @patch('DataSource.dummy.leapidatasource.LeapiDataSource.delete')
    def test_delete(self, dsmock):
        from dyncode import Publication, Numero, LeObject, LeType, LeRelation
        
        args = [
            Publication(1),
            Numero(5),
            LeObject(51),
            LeRelation(1337),
        ]

        for instance in args:
            instance.delete()
            dsmock.assert_called_once_with(instance.__class__, instance.uidget())
            dsmock.reset_mock()
            
