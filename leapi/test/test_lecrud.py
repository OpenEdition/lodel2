"""
    Tests for _LeCrud and LeCrud
"""

import unittest
from unittest import TestCase
from unittest.mock import patch

import EditorialModel
import leapi
import leapi.test.utils
from leapi.lecrud import _LeCrud

## @brief Test LeCrud methods
# @note those tests need the full dynamically generated code
class LeCrudTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leapi.test.utils.cleanup(cls.tmpdir)

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
            res = dyncode.LeCrud._split_filter(query)
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
                dyncode.LeCrud._split_filter(query)

    def test_field_is_relational(self):
        """ Testing the test to check if a field is relational """
        from dyncode import LeCrud

        test_fields = {
            'superior.parent': True,
            'subordinate.parent': True,
            'foofoo.foo': False,
        }

        for field, eres in test_fields.items():
            self.assertEqual(LeCrud._field_is_relational(field), eres)

    def test_check_datas(self):
        """ testing the check_datas* methods """
        from dyncode import Publication, Numero, LeObject

        datas = { 'titre':'foobar' }
        Numero.check_datas_value(datas, False, False)
        Numero.check_datas_value(datas, True, False)
        with self.assertRaises(leapi.lecrud.LeApiDataCheckError):
            Numero.check_datas_value({}, True)

    def test_prepare_filters(self):
        """ Testing the _prepare_filters() method """
        from dyncode import Publication, Numero, LeObject, Personnes
        
        #Simple filters
        filters = [
            'lodel_id = 1',
            'superior.parent  > 2'
        ]

        filt, rfilt = Numero._prepare_filters(filters)
        self.assertEqual(filt, [('lodel_id', '=', '1')])
        self.assertEqual(rfilt, [((leapi.leobject.REL_SUP,'parent'), '>', '2')])
        
        #All fields, no relationnal and class given
        filters = []
        res_filt = []
        for field in Numero._fields:
            filters.append('%s=1'%field)
            res_filt.append((field, '=', '1'))

        filt, rfilt = Publication._prepare_filters(filters)
        self.assertEqual(rfilt, [])
        self.assertEqual(filt, res_filt)
        
        #Mixed type filters (tuple and string)
        filters = [
            ('lodel_id', '<=', '0'),
            'subordinate.parent = 2',
        ]
        
        filt, rfilt = Numero._prepare_filters(filters)
        self.assertEqual(filt, [('lodel_id', '<=', '0')])
        self.assertEqual(rfilt, [((leapi.leobject.REL_SUB,'parent'), '=', '2')])
 
    def test_prepare_filters_invalid(self):
        """ Testing the _prepare_filters() method """
        from dyncode import LeCrud, Publication, Numero, Personnes, LeObject

        #Numero fields filters but no letype nor leclass given
        filters = []
        res_filt = []
        for field in Numero._fields:
            filters.append('%s=1'%field)
            res_filt.append((field, '=', '1'))
        
        with self.assertRaises(leapi.lecrud.LeApiDataCheckError):
            LeObject._prepare_filters(filters)


        #simply invalid filters
        filters = ['hello world !']
        with self.assertRaises(ValueError):
            Personnes._prepare_filters(filters)
    

    # 
    #   Tests mocking the datasource
    # 

    @patch('leapi.datasources.dummy.DummyDatasource.insert')
    def test_insert(self, dsmock):
        from dyncode import Publication, Numero, LeObject, Personne, Article
        ndatas = [
            (Numero, {'titre' : 'FooBar'}),
            (Numero, {'titre':'hello'}),
            (Personne, {'nom':'world', 'prenom':'hello'}),
            (Article, {'titre': 'Ar Boof', 'soustitre': 'Wow!'}),
        ]
        for lecclass, ndats in ndatas:
            lecclass.insert(ndats)
            dsmock.assert_called_once_with(lecclass, **ndats)
            dsmock.reset_mock()

            lecclass.insert(ndats)
            dsmock.assert_called_once_with(lecclass, **ndats)
            dsmock.reset_mock()
    
    ## @todo try failing on inserting from LeClass child or LeObject
    @patch('leapi.datasources.dummy.DummyDatasource.insert')
    def test_insert_fails(self, dsmock):
        from dyncode import Publication, Numero, LeObject, Personne, Article
        ndatas = [
            (Numero, dict()),
            (Numero, {'titre':'hello', 'lodel_id':42}),
            (Numero, {'tititre': 'hehello'}),
            (Personne, {'titre':'hello'}),
            (Article, {'titre': 'hello'}),
        ]
        for lecclass, ndats in ndatas:
            with self.assertRaises(leapi.lecrud.LeApiDataCheckError, msg="But trying to insert %s as %s"%(ndats, lecclass.__name__)):
                lecclass.insert(ndats)
                assert not dsmock.called
        pass
    
    @patch('leapi.datasources.dummy.DummyDatasource.update')
    def test_update(self, dsmock):
        from dyncode import Publication, Numero, LeObject
        
        args_l = [
            (
                Numero,
                {'lodel_id':'1'},
                {'titre': 'foobar'},

                [('lodel_id', '=', 1)],
                []
            ),
        ]

        for ccls, initarg, qdatas, efilters, erelfilters in args_l:
            obji = ccls(**initarg)
            obji.update(qdatas)
            dsmock.assert_called_once_with(ccls, efilters, erelfilters, **qdatas)
    
    ## @todo test invalid get
    @patch('leapi.datasources.dummy.DummyDatasource.select')
    def test_get(self, dsmock):
        from dyncode import Publication, Numero, LeObject, Textes
        
        args = [
            (
                Numero,
                ['lodel_id', 'superior.parent'],
                ['titre != "foobar"'],

                ['lodel_id', (leapi.leobject.REL_SUP, 'parent')],
                [('titre','!=', '"foobar"')],
                []
            ),
            (
                Numero,
                ['lodel_id', 'titre', 'superior.parent', 'subordinate.translation'],
                ['superior.parent in  [1,2,3,4,5]'],

                ['lodel_id', 'titre', (leapi.leobject.REL_SUP,'parent'), (leapi.leobject.REL_SUB, 'translation')],
                [],
                [( (leapi.leobject.REL_SUP, 'parent'), ' in ', '[1,2,3,4,5]')]
            ),
            (
                Numero,
                [],
                [],

                Numero._fields,
                [],
                []
            ),
            (
                Textes,
                ['lodel_id', 'titre', 'soustitre', 'superior.parent'],
                ['titre != "foobar"'],

                ['lodel_id', 'titre', 'soustitre', (leapi.leobject.REL_SUP, 'parent')],
                [('titre','!=', '"foobar"')],
                [],
            ),
            (
                LeObject,
                ['lodel_id'],
                [],

                ['lodel_id'],
                [],
                [],
            ),
        ]

        for callcls, field_list, filters, fl_ds, filters_ds, rfilters_ds in args:
            callcls.get(filters, field_list)
            dsmock.assert_called_with(callcls, fl_ds, filters_ds, rfilters_ds)
            dsmock.reset_mock()


