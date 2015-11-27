"""
    Tests for _LeRelation object family
"""

import unittest
from unittest import TestCase
from unittest.mock import patch

import EditorialModel
import leapi
import leapi.test.utils
from leapi.lecrud import _LeCrud

class LeRelationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leapi.test.utils.cleanup(cls.tmpdir)
    
    @unittest.skip("Wating LeRelation._prepare_filters() to unskip")
    def test_prepare_filters(self):
        """ Testing the _prepare_filters() method """
        from dyncode import Numero, LeObject, LeRelation
        
        filters = [
            (
                'rank = 1',
                ('rank', '=', '1')
            ),
            (
                'nature = "parent"',
                ('nature', '=', '"parent"')
            ),
            (
                'lesup = 21',
                ('lesup', '=', LeObject(21))
            ),
            (
                'lesub = 22',
                ('lesub', '=', LeObject(22))
            ),
            (
                ('rank', '=', '1'),
                ('rank', '=', '1'),
            ),
            (
                ('lesup', '=', LeObject(21)),
                ('lesup', '=', LeObject(21)),
            ),
            (
                ('lesub', '=', Numero(42)),
                ('lesub', '=', Numero(42)),
            ),
        ]
        
        for filter_arg, filter_res in filters:
            res, rel_res = LeRelation._prepare_filters([filter_arg])
            self.assertEqual(len(res), 1)
            self.assertEqual(len(rel_res), 0)
            res = res[0]
            
            for i in range(3):
               self.assertEqual(filter_res[i], res[i], "%s != %s"%(filter_res, res))

    @unittest.skip("Wait LeRelation._prepare_filters() and LeRelation.delete() to unskip")
    @patch('leapi.datasources.dummy.DummyDatasource.delete')
    def test_delete(self, dsmock):
        """ Testing LeHierarch insert method """
        from dyncode import LeCrud, Publication, Numero, Personnes, LeObject, Rubrique, LeHierarch, LeRelation
        
        LeRelation.delete([LeRelation.sup_filter(Numero(42)), 'nature = "parent"'], 'LeHierarch')
        dsmock.assert_called_once_with(LeHierarch, [('lesup', '=', Numero(42)), ('nature','=','parent')])
        dsmock.reset_mock()


class LeHierarch(LeRelationTestCase):
    
    @unittest.skip("Wait for  LeRelation._prepare_filters() to unskip")
    @patch('leapi.datasources.dummy.DummyDatasource.select')
    def test_get(self, dsmock):
        """ Tests the LeHierarch.get() method """
        from dyncode import LeCrud, Publication, Numero, Personnes, LeObject, Rubrique, LeHierarch, LeRelation

        queries = [
            (
                ['lesup = 42', 'lesub = 24'], #filters
                ['lesup', 'lesub', 'nature', 'rank'], #field_l

                LeHierarch, #target
                ['lesup', 'lesub', 'nature', 'rank'], #field_ds
                [('lesup','=',LeObject(42)), ('lesub', '=', LeObject(24))], #filters_ds
                [], #rfilters_ds

            ),
            (
                [ LeRelation.sup_filter(Numero(42)) ],
                [],

                LeHierarch,
                [ 'nature', 'rank', 'lesub', 'depth', 'lesup'],
                [('lesup', '=', Numero(42))],
                [],
            ),
        ]

        for filters, field_l, target, field_ds, filters_ds, rfilters_ds in queries:
            eargs = (filters, field_l, target, field_ds, filters_ds, rfilters_ds)

            LeHierarch.get(filters, field_l)
            cargs = dsmock.call_args

            self.assertEqual(len(cargs), 2)
            cargs=cargs[0]

            self.assertEqual(cargs[0], target, "%s != %s"%(cargs, eargs))
            self.assertEqual(set(cargs[1]), set(field_ds), "%s != %s"%(cargs, eargs))
            self.assertEqual(cargs[2], filters_ds, "%s != %s"%(cargs, eargs))
            self.assertEqual(cargs[3], rfilters_ds, "%s != %s"%(cargs, eargs))

            dsmock.reset_mock()
    
    @unittest.skip("Wait for  LeRelation._prepare_filters() to unskip")
    @patch('leapi.datasources.dummy.DummyDatasource.insert')
    def test_insert(self, dsmock):
        """ Testing LeHierarch insert method """
        from dyncode import LeCrud, Publication, Numero, Personnes, LeObject, Rubrique, LeHierarch, LeRelation
        queries = [
            {
                'lesup': Rubrique(7),
                'lesub': Numero(42),
                'nature': 'parent',
            },
            {
                'lesup': 7,
                'lesub': 42,
                'nature': 'parent',
            },
            {
                'lesup': LeObject(7),
                'lesub': LeObject(42),
                'nature': 'parent',
            },
            {
                'lesup': LeObject(7),
                'lesub': 42,
                'nature': 'parent',
            }
        ]
        for query in queries:
            LeHierarch.insert(query)
            dsmock.assert_called_once_with(LeHierarch, **query)
            dsmock.reset_mock()

            LeRelation.insert(query, 'LeHierarch')
            dsmock.assert_called_once_with(LeHierarch, **query)
            dsmock.reset_mock()
    

    @unittest.skip("Wait for LeRelation.delete()")
    @patch('leapi.datasources.dummy.DummyDatasource.delete')
    def test_delete(self, dsmock):
        """ Testing LeHierarch insert method """
        from dyncode import LeCrud, Publication, Numero, Personnes, LeObject, Rubrique, LeHierarch, LeRelation
        rel = LeHierarch(10)
        rel.delete()
        dsmock.assert_called_once_with(LeHierarch, [(LeHierarch.uidname(), '=', 10)], [])
        
    
    @unittest.skip("Wait for LeRelation.update() to unskip")
    @patch('leapi.datasources.dummy.DummyDatasource.update')
    def test_update(self, dsmock):
        """ test LeHierach update method"""
        from dyncode import LeHierarch
        with self.assertRaises(NotImplementedError):
            LeHierarch.update({})
            
    

class LeRel2TypeTestCase(LeRelationTestCase):
    
    @unittest.skip("Wait implementation to unskip")
    @patch('leapi.datasources.dummy.DummyDatasource.insert')
    def test_insert(self, dsmock):
        """ test LeHierach update method"""
        from dyncode import LeObject, Article, Textes, Personne, Personnes, LeHierarch, LeRel2Type, Rel_textes2personne

        queries = [
            {
                'lesup': Article(42),
                'lesub': Personne(24),
                'adresse': None,
            },
            {
                'lesup': Textes(42),
                'lesub': Personne(24),
                'adresse': None,
            },
            {
                'lesup': 42,
                'lesub': Personne(24),
                'adresse': None,
            },

            {
                'lesup': Article(42),
                'lesub': Personnes(24),
                'adresse': "bar",
            },
            {
                'lesup': Textes(42),
                'lesub': Personnes(24),
                'adresse': "foo",
            },
        ]

        for query in queries:
            Rel_textes2personne.insert(query)

            eres = {'nature': None}
            eres.uopdate(query)

            dsmock.assert_called_once_with(Rel_textes2personne, **eres)

