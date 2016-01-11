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
    
    @unittest.skip("Obsolete but may be usefull for datasources tests")
    def test_prepare_targets(self):
        """ Testing _prepare_targets() method """
        from dyncode import Publication, Numero, LeObject

        test_v = {
            (None, None) : (None, None),

            (Publication, Numero): (Publication, Numero),
            (Publication, None): (Publication, None),
            (None, Numero): (Publication, Numero),

            (Publication,'Numero'): (Publication, Numero),
            ('Publication', Numero): (Publication, Numero),

            ('Publication', 'Numero'): (Publication, Numero),
            ('Publication', None): (Publication, None),
            (None, 'Numero'): (Publication, Numero),
        }

        for (leclass, letype), (rleclass, rletype) in test_v.items():
            self.assertEqual((rletype,rleclass), LeObject._prepare_targets(letype, leclass))

    @unittest.skip("Obsolete but may be usefull for datasources tests")
    def test_invalid_prepare_targets(self):
        """ Testing _prepare_targets() method with invalid arguments """
        from dyncode import Publication, Numero, LeObject, Personnes
        
        test_v = [
            ('',''),
            (Personnes, Numero),
            (leapi.leclass.LeClass, Numero),
            (Publication, leapi.letype.LeType),
            ('foobar', Numero),
            (Publication, 'foobar'),
            (Numero, Numero),
            (Publication, Publication),
            (None, Publication),
            ('foobar', 'foobar'),
            (42,1337),
            (type, Numero),
            (LeObject, Numero),
            (LeObject, LeObject),
            (Publication, LeObject),
        ]

        for (leclass, letype) in test_v:
            with self.assertRaises(ValueError):
                LeObject._prepare_targets(letype, leclass)

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
    
    @patch('DataSource.dummy.leapidatasource.DummyDatasource.insert')
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

    @unittest.skip("Wait FieldTypes modification (cf. #90) and classmethod capabilities for update")
    @patch('DataSource.dummy.leapidatasource.DummyDatasource.update')
    def test_update(self, dsmock):
        from dyncode import Publication, Numero, LeObject

        args = [
            (   ['lodel_id = 1'],
                {'titre':'foobar'},
                [('lodel_id','=','1')],
                []
            ),
            (   ['superior.parent in [1,2,3,4,5,6]', 'titre != "FooBar"'],
                {'titre':'FooBar'},
                [( 'titre','!=','"FooBar"')],
                [( (leapi.leobject.REL_SUP, 'parent') ,' in ', '[1,2,3,4,5,6]')]
            ),
        ]

        for filters, datas, ds_filters, ds_relfilters in args:
            LeObject.update(Numero, filters, datas)
            dsmock.assert_called_once_with(Numero, Publication, ds_filters, ds_relfilters, datas)
            dsmock.reset_mock()

            LeObject.update('Numero', filters, datas)
            dsmock.assert_called_once_with(Numero, Publication, ds_filters, ds_relfilters, datas)
            dsmock.reset_mock()
    
    @patch('DataSource.dummy.leapidatasource.DummyDatasource.delete')
    def test_delete(self, dsmock):
        from dyncode import Publication, Numero, LeObject, LeType

        args = [
            (
                'Numero',
                ['lodel_id=1'],
                [('lodel_id', '=', '1'), ('type_id', '=', Numero._type_id)],
                []
            ),
            (
                'Publication',
                ['subordinate.parent not in [1,2,3]', 'titre = "titre nul"'],
                [('titre','=', '"titre nul"'), ('class_id', '=', Publication._class_id)],
                [( (leapi.leobject.REL_SUB, 'parent'), ' not in ', '[1,2,3]')]
            ),
        ]

        for classname, filters, ds_filters, ds_relfilters in args:
            ccls = LeObject.name2class(classname)

            LeObject.delete(filters, classname)
            dsmock.assert_called_once_with(ccls, ds_filters, ds_relfilters)
            dsmock.reset_mock()
            
            if not (LeType in ccls.__bases__): #tests for calls with a LeClass child
                ccls.delete(filters)
                dsmock.assert_called_once_with(ccls, ds_filters, ds_relfilters)
                dsmock.reset_mock()
        
