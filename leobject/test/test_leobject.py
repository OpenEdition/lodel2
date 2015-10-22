"""
    Tests for _LeObject
"""

import unittest
from unittest import TestCase

import EditorialModel
import leobject
import leobject.test.utils
from leobject.leobject import _LeObject

## Testing static methods that don't need the generated code
class _LeObjectTestCase(TestCase):
    
    def test_split_query_filter(self):
        """ Tests the _split_filter() classmethod """
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
            res = _LeObject._split_filter(query)
            self.assertEqual(res, result, "When parsing the query : '%s' the returned value is different from the expected '%s'"%(query, result))

    def test_invalid_split_query_filter(self):
        """ Testing the _split_filter() method with invalid queries """
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
                _LeObject._split_filter(query)

## Testing methods that need the generated code
# @todo mock the datasource to test the get, update, delete and insert methods
class LeObjectTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leobject.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leobject.test.utils.cleanup(cls.tmpdir)

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
        self.assertEqual(rfilt, [('parent', '>', '2')])
        
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
            'superior.parent = 2',
        ]
        
        filt, rfilt = LeObject._prepare_filters(filters, Numero, None)
        self.assertEqual(filt, [('lodel_id', '<=', '0')])
        self.assertEqual(rfilt, [('parent', '=', '2')])

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
    
