"""
    Tests for _LeRelation object family
"""

import unittest
from unittest import TestCase
from unittest.mock import patch
from collections import OrderedDict

import EditorialModel
import DataSource.dummy
import leapi
import leapi.test.utils
import leapi.lecrud as lecrud
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
                'superior = 21',
                ('superior', '=', LeObject(21))
            ),
            (
                'subordinate = 22',
                ('subordinate', '=', LeObject(22))
            ),
            (
                ('rank', '=', '1'),
                ('rank', '=', '1'),
            ),
            (
                ('superior', '=', LeObject(21)),
                ('superior', '=', LeObject(21)),
            ),
            (
                ('subordinate', '=', Numero(42)),
                ('subordinate', '=', Numero(42)),
            ),
        ]
        
        for filter_arg, filter_res in filters:
            res, rel_res = LeRelation._prepare_filters([filter_arg])
            self.assertEqual(len(res), 1)
            self.assertEqual(len(rel_res), 0)
            res = res[0]

            for i in range(3):
                self.assertEqual(filter_res[i], res[i], "%s != %s"%(filter_res, res))

    @patch('DataSource.dummy.leapidatasource.DummyDatasource.delete')
    def test_delete(self, dsmock):
        """ Testing LeHierarch insert method """
        from dyncode import LeCrud, Publication, Numero, Personnes, LeObject, Rubrique, LeHierarch, LeRelation
        
        LeRelation.delete([LeRelation.sup_filter(Numero(42)), 'nature = "parent"'], 'LeHierarch')
        dsmock.assert_called_once_with(LeHierarch, [('superior', '=', Numero(42)), ('nature','=','"parent"')])
        dsmock.reset_mock()


class LeHierarch(LeRelationTestCase):
    
    @patch('DataSource.dummy.leapidatasource.DummyDatasource.select')
    def test_get(self, dsmock):
        """ Tests the LeHierarch.get() method without limit group order etc."""
        from dyncode import LeCrud, Publication, Numero, Personnes, LeObject, Rubrique, LeHierarch, LeRelation

        queries = [
            (
                ['superior = 42', 'subordinate = 24'], #filters
                ['superior', 'subordinate', 'nature', 'rank'], #field_l

                LeHierarch, #target
                ['superior', 'subordinate', 'nature', 'rank'], #field_ds
                [('superior','=',LeObject(42)), ('subordinate', '=', LeObject(24))], #filters_ds
                [], #rfilters_ds

            ),
            (
                [ LeRelation.sup_filter(Numero(42)) ],
                [],

                LeHierarch,
                [ 'nature', 'rank', 'subordinate', 'depth', 'superior', 'id_relation'],
                [('superior', '=', Numero(42))],
                [],
            ),
        ]

        for filters, field_l, target, field_ds, filters_ds, rfilters_ds in queries:
            eargs = (filters, field_l, target, field_ds, filters_ds, rfilters_ds)

            LeHierarch.get(filters, field_l)
            cargs = dsmock.call_args

            self.assertEqual(len(cargs), 2)
            cargs=cargs[1]
            self.assertEqual(cargs['target_cls'], target, "%s != %s"%(cargs, eargs))
            self.assertEqual(set(cargs['field_list']), set(field_ds), "%s != %s"%(cargs, eargs))
            self.assertEqual(cargs['filters'], filters_ds, "%s != %s"%(cargs, eargs))
            self.assertEqual(cargs['rel_filters'], rfilters_ds, "%s != %s"%(cargs, eargs))

            dsmock.reset_mock()
    
    @patch('DataSource.dummy.leapidatasource.DummyDatasource.insert')
    def test_insert(self, dsmock):
        """ Testing LeHierarch insert method """
        from dyncode import LeCrud, Publication, Numero, Personnes, LeObject, Rubrique, LeHierarch, LeRelation
        queries = [
            (
                {
                    'superior': Rubrique(7, class_id = Rubrique._class_id, type_id = Rubrique._type_id),
                    'subordinate': Numero(42, class_id = Numero._class_id, type_id = Numero._type_id),
                    'nature': 'parent',
                },
                {
                    'superior': Rubrique(7),
                    'subordinate': Numero(42),
                    'nature': 'parent',
                },
            ),
        ]
        """ # Those tests are not good
            (
                {
                    'superior': 7,
                    'subordinate': 42,
                    'nature': 'parent',
                },
                {
                    'superior': LeObject(7),
                    'subordinate': LeObject(42),
                    'nature': 'parent',
                }
            ),
            (
                {
                    'superior': LeObject(7),
                    'subordinate': LeObject(42),
                    'nature': 'parent',
                },
                {
                    'superior': LeObject(7),
                    'subordinate': LeObject(42),
                    'nature': 'parent',
                }
            ),
            (
                {
                    'superior': LeObject(7),
                    'subordinate': 42,
                    'nature': 'parent',
                },
                {
                    'superior': LeObject(7),
                    'subordinate': LeObject(42),
                    'nature': 'parent',
                }
            )
        ]
        """
        for query, equery in queries:
            equery['rank'] = 1
            equery['depth'] = None

            LeHierarch.insert(query)
            dsmock.assert_called_once_with(LeHierarch, **equery)
            dsmock.reset_mock()

            LeRelation.insert(query, 'LeHierarch')
            dsmock.assert_called_once_with(LeHierarch, **equery)
            dsmock.reset_mock()
    

    @patch('DataSource.dummy.leapidatasource.DummyDatasource.delete')
    def test_delete(self, dsmock):
        """ Testing LeHierarch delete method """
        from dyncode import LeCrud, Publication, Numero, Personnes, LeObject, Rubrique, LeHierarch, LeRelation
        rel = LeHierarch(10)
        rel.delete()
        dsmock.assert_called_once_with(LeHierarch, [(LeHierarch.uidname(), '=', 10)], [])
        
    
    @unittest.skip("Wait for LeRelation.update() to unskip")
    @patch('DataSource.dummy.leapidatasource.DummyDatasource.update')
    def test_update(self, dsmock):
        """ test LeHierach update method"""
        from dyncode import LeHierarch
        with self.assertRaises(NotImplementedError):
            LeHierarch.update({})
            
    

class LeRel2TypeTestCase(LeRelationTestCase):
    
    @patch('DataSource.dummy.leapidatasource.DummyDatasource.insert')
    def test_insert(self, dsmock):
        """ test LeHierach update method"""
        from dyncode import LeObject, Article, Textes, Personne, Personnes, LeHierarch, LeRel2Type, Rel_Textes2Personne

        queries = [
            {
                'superior': Article(42),
                'subordinate': Personne(24),
                'adresse': None,
            },
            {
                'superior': Textes(42),
                'subordinate': Personne(24),
                'adresse': None,
            },
            {
                'superior': Article(42),
                'subordinate': Personne(24),
                'adresse': "bar",
            },
            {
                'superior': Textes(42),
                'subordinate': Personne(24),
                'adresse': "foo",
            },
        ]

        for query in queries:
            Rel_Textes2Personne.insert(query)

            eres = {'nature': None, 'depth': None, 'rank': 0}
            eres.update(query)
            for fname in ('superior', 'subordinate'):
                if isinstance(eres[fname], int):
                    eres[fname] = LeObject(eres[fname])

            dsmock.assert_called_once_with(Rel_Textes2Personne, **eres)
            dsmock.reset_mock()

            LeRel2Type.insert(query, "Rel_Textes2Personne")

            dsmock.assert_called_once_with(Rel_Textes2Personne, **eres)
            dsmock.reset_mock()

    @patch('DataSource.dummy.leapidatasource.DummyDatasource.insert')
    def test_insert_fails(self, dsmock):
        """ test LeHierach update method"""
        from dyncode import LeObject, Rubrique, Numero, Article, Textes, Personne, Personnes, LeHierarch, LeRel2Type, Rel_Textes2Personne

        queries = [
            {
                'superior': Rubrique(42),
                'subordinate': Personne(24),
                'adresse': None,
            },
            {
                'adresse': None,
            },
            {
                'superior': Rubrique(42),
                'subordinate': Rubrique(24),
                'adresse': None,
            },
            {
                'superior': Article(42),
                'subordinate': Numero(24),
                'adresse': 'foo',
            },
            {
                'id_relation': 1337,
                'superior': Article(42),
                'subordinate': Numero(24),
                'adresse': 'foo',
            },
        ]

        for query in queries:
            try:
                LeRel2Type.insert(query, 'Rel_textes2personne')
                self.fail("No exception raised")
            except Exception as e:
                if not isinstance(e, lecrud.LeApiErrors) and not isinstance(e, lecrud.LeApiDataCheckError):
                    self.fail("Bad exception raised : ", e)

            try:
                Rel_Textes2Personne.insert(query)
                self.fail("No exception raised")
            except Exception as e:
                if not isinstance(e, lecrud.LeApiErrors) and not isinstance(e, lecrud.LeApiDataCheckError):
                    self.fail("Bad exception raised : ", e)
