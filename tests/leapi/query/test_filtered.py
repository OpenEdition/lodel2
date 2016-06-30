import unittest

import tests.loader_utils
from tests.leapi.query.utils import dyncode_module as dyncode

from lodel.leapi.exceptions import *
from lodel.leapi.query import LeDeleteQuery, LeUpdateQuery, LeGetQuery

class LeFilteredQueryTestCase(unittest.TestCase):

    q_classes = [ LeDeleteQuery, LeUpdateQuery, LeGetQuery ]

    def test_filters(self):
        """ Testing FilteredQuery filters handling """
        test_datas = [  (   'lodel_id = 42',
                            (   [('lodel_id','=',42)],
                                [])),
                        (   'lodel_id <= 42',
                            (   [('lodel_id','<=',42)],
                                [])),
                        (   ['lodel_id <= 42'],
                            (   [('lodel_id','<=',42)],
                                [])),
                        (   ('lodel_id <= 42',),
                            (   [('lodel_id','<=',42)],
                                [])),
                        (   ['lodel_id <= 42','lodel_id >= 33'],
                            (   [   ('lodel_id','<=',42),
                                    ('lodel_id', '>=',33)],
                                [])),
        ]
        for q_class in self.q_classes:
            for q_filter_arg, e_qfilter in test_datas:
                get_q = q_class(dyncode.Publication, q_filter_arg)
                self.assertEqual(
                    sorted(get_q.dump_infos()['query_filter'][0]),
                    sorted(e_qfilter[0]))

    def test_invalid_filters(self):
        """ Testing invalid filters detection """
        invalid_filters = ( 'lodel_id',
                            '',
                            '"',
                            "'",
                            "not_exists != bar",
                            "lodel_id # bar",
                            "lodel_id == bar",
                            "lodel_id =! bar",
                            "lodel_id >> bar",
                            "lodel_id ind 42,43",
                            "lodel_id llike 42",
                            ('lodel_id', '', '42'),
        )
        for invalid_filter in invalid_filters:
            for q_class in self.q_classes:
                with self.assertRaises( LeApiDataCheckErrors,
                                        msg="for filter '%s'" % (invalid_filter,)):
                    q_class(dyncode.Publication, invalid_filter)
            
        
    def test_filters_operators(self):
        """ Testing FilteredQuery filters operator recognition """
        ops = [         '=',
                        '<=',
                        '>=',
                        '!=',
                        '<',
                        '>',
                        'in',
                        'not in',
                        'like',
                        'not like']
        values = (  42,
                    'not in',
                    'in',
                    'like',
                    '=',
                    '!=',
                    "'",
                    '"',
                    '"hello world !"')
        for q_class in self.q_classes:
            for op in ops:
                for v in values:
                    get_q = q_class(    dyncode.Publication,
                                        'lodel_id %s %s' % (op,v))
                    self.assertEqual(   get_q.dump_infos()['query_filter'],
                                        ([('lodel_id',op,v)],[]))
    
    def test_rel_filters(self):
        """ Testing relational filters recognition """
        test_datas = [  (   dyncode.Subsection,
                            'parent.title = 42',
                            (   [],
                                [(('parent', {dyncode.Section: 'title'}), '=', '42')])),
                        (   dyncode.Section,
                            'childs.title = 42',
                            (   [],
                                [(('childs', {dyncode.Subsection: 'title'}), '=', '42')]))
                        ]

        for le_class, q_filter_arg, e_qfilter in test_datas:
            get_q = LeGetQuery(le_class, q_filter_arg)
            qinfos = get_q.dump_infos()
            self.assertEqual(   qinfos['query_filter'],
                                e_qfilter)


class LeFilteredQueryMultiDataHandlerTestCase(unittest.TestCase):
    """ Testing LeFilteredQuery behavior when relational fields implies
        different datasources """

    q_classes = [LeDeleteQuery, LeUpdateQuery, LeGetQuery]
    
    def test_basic(self):
        """ Testing a LeGetQuery with a relationnal field implying another
            datasource """
        getq = LeGetQuery(
            dyncode.Indextheme,
            "texts.title = super titre !")
        qinfos = getq.dump_infos()
        # The single query filter should be in subquery
        self.assertEqual(qinfos['query_filter'], ([],[]))
        self.assertEqual(len(qinfos['subqueries']), 1)
        rfield, subq = qinfos['subqueries'][0]
        # Checking subquery
        self.assertEqual(rfield, 'texts') # The reference field of the subquery
        qinfos = subq.dump_infos()
        self.assertEqual(qinfos['target_class'], dyncode.Text)
        self.assertEqual(
            qinfos['query_filter'],
            ([('title', '=', 'super titre !')],[])) 
        self.assertEqual(qinfos['field_list'], ['title'])

    def test_uid_as_ref_field(self):
        """ Testing basic query optimisation with a relationnal filter 
            with lodel_id as referenced field"""
        getq = LeGetQuery(
            dyncode.Indextheme,
            "texts.lodel_id in 1,2,3,42")
        qinfos = getq.dump_infos()
        #No subqueries should be created because referenced field is 
        #the referenced class UID
        self.assertEqual(qinfos['subqueries'],[])
        self.assertEqual(
            qinfos['query_filter'], 
            ([('texts', 'in', '1,2,3,42')], []))

    def test_implicit_uid(self):
        """ Testing query with an UID as implicit referenced field for a 
            relationnal filter """
        getq = LeGetQuery(
            dyncode.Indextheme,
            "texts in 13,1337,357,80")
        qinfos = getq.dump_infos()
        #No subqueries expected
        self.assertEqual(qinfos['subqueries'],[])
        self.assertEqual(
            qinfos['query_filter'], 
            ([('texts', 'in', '13,1337,357,80')], []))

    def test_same_datasource(self):
        """ Testing a query with relationnal filters concerning only one
            datasource to check for 'false positive' in subqueries creation """ 
        getq = LeGetQuery(
            dyncode.Text,
            "linked_persons.fullname = John Doe")
        qinfos = getq.dump_infos()
        self.assertEqual(qinfos['subqueries'],[])
        self.assertEqual(
            qinfos['query_filter'], 
            (   [],
                [(('linked_persons', {dyncode.Person:'fullname'}),'=', 'John Doe')]))

