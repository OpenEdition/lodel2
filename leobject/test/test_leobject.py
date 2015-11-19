"""
    Tests for _LeObject and LeObject
"""

import unittest
from unittest import TestCase
from unittest.mock import patch

import EditorialModel
import leobject
import leobject.test.utils
from leobject.leobject import _LeObject

## Testing methods that need the generated code
class LeObjectTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leobject.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leobject.test.utils.cleanup(cls.tmpdir)

    def test_split_query_filter(self):
        """ Tests the _split_filter() classmethod """
        import dyncode
        query_results = {
            'Hello = world' : ('Hello', '=', 'world'),
            'hello <= "world"': ('hello', '<=', '"world"'),
            '_he42_ll-o >= \'world"': ('_he42_ll-o', '>=', '\'world"'),
            'foo in ["foo", 42, \'bar\']': ('foo', ' in ', '["foo", 42, \'bar\']'),
            ' bar42              < 42': ('bar42', '<', '42'),
            ' _hidden > 1337': ('_hidden', '>', '1337'),
            '_42 not in foobar': ('_42', ' not in ', 'foobar'),
            'hello                       in      foo':('hello', ' in ', 'foo'),
            "\t\t\thello\t\t\nin\nfoo\t\t\n\t":('hello', ' in ', 'foo'),
            "hello \nnot\tin \nfoo":('hello', ' not in ', 'foo'),
            'hello != bar':('hello', '!=', 'bar'),
            'hello = "world>= <= != in not in"': ('hello', '=', '"world>= <= != in not in"'),
            'superior.parent = 13': ('superior.parent', '=', '13'),
        }
        for query, result in query_results.items():
            res = dyncode.LeObject._split_filter(query)
            self.assertEqual(res, result, "When parsing the query : '%s' the returned value is different from the expected '%s'"%(query, result))

    def test_invalid_split_query_filter(self):
        """ Testing the _split_filter() method with invalid queries """
        import dyncode
        invalid_queries = [
            '42 = 42',
            '4hello = foo',
            'foo == bar',
            'hello >> world',
            'hello =    ',
            ' = world',
            '=',
            '42',
            '"hello" = world',
            'foo.bar = 15',
        ]
        for query in invalid_queries:
            with self.assertRaises(ValueError, msg='But the query was not valid : "%s"'%query):
                dyncode.LeObject._split_filter(query)

    def test_uid2leobj(self):
        """ Testing _Leobject.uid2leobj() """
        import dyncode
        for i in dyncode.LeObject._me_uid.keys():
            cls = dyncode.LeObject.uid2leobj(i)
            if leobject.letype.LeType in cls.__bases__:
                self.assertEqual(i, cls._type_id)
            elif leobject.leclass.LeClass in cls.__bases__:
                self.assertEqual(i, cls._class_id)
            else:
                self.fail("Bad value returned : '%s'"%cls)
        i=10
        while i in dyncode.LeObject._me_uid.keys():
            i+=1
        with self.assertRaises(KeyError):
            dyncode.LeObject.uid2leobj(i)
    
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

    def test_invalid_prepare_targets(self):
        """ Testing _prepare_targets() method with invalid arguments """
        from dyncode import Publication, Numero, LeObject, Personnes
        
        test_v = [
            ('',''),
            (Personnes, Numero),
            (leobject.leclass.LeClass, Numero),
            (Publication, leobject.letype.LeType),
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

    def test_check_fields(self):
        """ Testing the _check_fields() method """
        from dyncode import Publication, Numero, LeObject, Personnes
        
        #Valid fields given
        LeObject._check_fields(None, Publication, Publication._fieldtypes.keys())
        LeObject._check_fields(Numero, None, Numero._fields)

        #Specials fields
        LeObject._check_fields(Numero, Publication,  ['lodel_id'])
        #Common fields
        LeObject._check_fields(None, None, EditorialModel.classtypes.common_fields.keys())

        #Invalid fields
        with self.assertRaises(leobject.leobject.LeObjectQueryError):
            LeObject._check_fields(None, None, Numero._fields)

    def test_prepare_filters(self):
        """ Testing the _prepare_filters() method """
        from dyncode import Publication, Numero, LeObject, Personnes
        
        #Simple filters
        filters = [
            'lodel_id = 1',
            'superior.parent  > 2'
        ]

        filt, rfilt = LeObject._prepare_filters(filters, Numero, None)
        self.assertEqual(filt, [('lodel_id', '=', '1')])
        self.assertEqual(rfilt, [((leobject.leobject.REL_SUP,'parent'), '>', '2')])
        
        #All fields, no relationnal and class given
        filters = []
        res_filt = []
        for field in Numero._fields:
            filters.append('%s=1'%field)
            res_filt.append((field, '=', '1'))

        filt, rfilt = LeObject._prepare_filters(filters, None, Publication)
        self.assertEqual(rfilt, [])
        self.assertEqual(filt, res_filt)
        
        #Mixed type filters (tuple and string)
        filters = [
            ('lodel_id', '<=', '0'),
            'subordinate.parent = 2',
        ]
        
        filt, rfilt = LeObject._prepare_filters(filters, Numero, None)
        self.assertEqual(filt, [('lodel_id', '<=', '0')])
        self.assertEqual(rfilt, [((leobject.leobject.REL_SUB,'parent'), '=', '2')])

    def test_prepare_filters_invalid(self):
        """ Testing the _prepare_filters() method """
        from dyncode import Publication, Numero, LeObject, Personnes

        #Numero fields filters but no letype nor leclass given
        filters = []
        res_filt = []
        for field in Numero._fields:
            filters.append('%s=1'%field)
            res_filt.append((field, '=', '1'))
        
        with self.assertRaises(leobject.leobject.LeObjectQueryError):
            LeObject._prepare_filters(filters, None, None)


        #simply invalid filters
        filters = ['hello world !']
        with self.assertRaises(ValueError):
            LeObject._prepare_filters(filters, None, None)

class LeObjectMockDatasourceTestCase(TestCase):
    """ Testing _LeObject using a mock on the datasource """

    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leobject.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leobject.test.utils.cleanup(cls.tmpdir)
    
    @patch('leobject.datasources.dummy.DummyDatasource.insert')
    def test_insert(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        ndatas = [
            [{'titre' : 'FooBar'}],
            [{'titre':'hello'},{'titre':'world'}],
        ]
        for ndats in ndatas:
            LeObject.insert(Numero,ndats)
            dsmock.assert_called_once_with(Numero, Publication, ndats)
            dsmock.reset_mock()

            LeObject.insert('Numero',ndats)
            dsmock.assert_called_once_with(Numero, Publication, ndats)
            dsmock.reset_mock()

    @patch('leobject.datasources.dummy.DummyDatasource.update')
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
                [( (leobject.leobject.REL_SUP, 'parent') ,' in ', '[1,2,3,4,5,6]')]
            ),
        ]

        for filters, datas, ds_filters, ds_relfilters in args:
            LeObject.update(Numero, filters, datas)
            dsmock.assert_called_once_with(Numero, Publication, ds_filters, ds_relfilters, datas)
            dsmock.reset_mock()

            LeObject.update('Numero', filters, datas)
            dsmock.assert_called_once_with(Numero, Publication, ds_filters, ds_relfilters, datas)
            dsmock.reset_mock()

    @patch('leobject.datasources.dummy.DummyDatasource.delete')
    def test_delete(self, dsmock):
        from dyncode import Publication, Numero, LeObject

        args = [
            (
                ['lodel_id=1'],
                [('lodel_id', '=', '1')],
                []
            ),
            (
                ['subordinate.parent not in [1,2,3]', 'titre = "titre nul"'],
                [('titre','=', '"titre nul"')],
                [( (leobject.leobject.REL_SUB, 'parent'), ' not in ', '[1,2,3]')]
            ),
        ]

        for filters, ds_filters, ds_relfilters in args:
            LeObject.delete(Numero, filters)
            dsmock.assert_called_once_with(Numero, Publication, ds_filters, ds_relfilters)
            dsmock.reset_mock()

            LeObject.delete('Numero', filters)
            dsmock.assert_called_once_with(Numero, Publication, ds_filters, ds_relfilters)
            dsmock.reset_mock()
        
    @patch('leobject.datasources.dummy.DummyDatasource.get')
    @unittest.skip('Dummy datasource doesn\'t fit anymore')
    def test_get(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        
        args = [
            (
                ['lodel_id', 'superior.parent'],
                ['titre != "foobar"'],

                ['lodel_id', (leobject.leobject.REL_SUP, 'parent')],
                [('titre','!=', '"foobar"')],
                []
            ),
            (
                ['lodel_id', 'titre', 'superior.parent', 'subordinate.translation'],
                ['superior.parent in  [1,2,3,4,5]'],

                ['lodel_id', 'titre', (leobject.leobject.REL_SUP,'parent'), (leobject.leobject.REL_SUB, 'translation')],
                [],
                [( (leobject.leobject.REL_SUP, 'parent'), ' in ', '[1,2,3,4,5]')]
            ),
            (
                [],
                [],

                Numero._fields,
                [],
                []
            ),
        ]

        for field_list, filters, fl_ds, filters_ds, rfilters_ds in args:
            LeObject.get(filters, field_list, Numero)
            dsmock.assert_called_with(Publication, Numero, fl_ds, filters_ds, rfilters_ds)
            dsmock.reset_mock()

    @patch('leobject.datasources.dummy.DummyDatasource.get')
    @unittest.skip('Dummy datasource doesn\'t fit anymore')
    def test_get_incomplete_target(self, dsmock):
        """ Testing LeObject.get() method with partial target specifier """
        from dyncode import Publication, Numero, LeObject

        args = [
            (
                ['lodel_id'],
                [],
                None,
                None,

                ['lodel_id', 'type_id'],
                [],
                [],
                None,
                None
            ),
            (
                [],
                [],
                None,
                None,

                list(EditorialModel.classtypes.common_fields.keys()),
                [],
                [],
                None,
                None
            ),
            (
                ['lodel_id'],
                [],
                None,
                Publication,

                ['lodel_id', 'type_id'],
                [],
                [],
                None,
                Publication
            ),
            (
                [],
                [],
                Numero,
                None,

                Numero._fields,
                [],
                [],
                Numero,
                Publication
            ),
        ]

        for field_list, filters, letype, leclass, fl_ds, filters_ds, rfilters_ds, letype_ds, leclass_ds in args:
            LeObject.get(filters, field_list, letype, leclass)
            dsmock.assert_called_with(leclass_ds, letype_ds, fl_ds, filters_ds, rfilters_ds)
            dsmock.reset_mock()

