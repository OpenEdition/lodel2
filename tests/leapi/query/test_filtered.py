import unittest

import tests.loader_utils
from tests.leapi.query.utils import dyncode_module as dyncode

from lodel.leapi.leobject import LeApiDataCheckError
from lodel.leapi.query import LeDeleteQuery, LeUpdateQuery, LeGetQuery

class LeGetQueryTestCase(unittest.TestCase):
    
    def test_init_default(self):
        """ Testing GetQuery instanciation default values"""
        tclass_list = [ dyncode.Object,
                        dyncode.Entry,
                        dyncode.Person,
                        dyncode.Text,
                        dyncode.Section,
                        dyncode.Publication,
                        dyncode.Text_Person,
        ]
        for tclass in tclass_list:
            get_q = LeGetQuery(tclass, [])
            qinfos = get_q.dump_infos()
            self.assertEqual(   set(qinfos['field_list']),
                                set(tclass.fieldnames(True)))
            self.assertEqual(   qinfos['limit'],
                                None)
            self.assertEqual(   qinfos['offset'],
                                0)
            self.assertEqual(   qinfos['group'],
                                None)
            self.assertEqual(   qinfos['order'],
                                None)
            self.assertEqual(   qinfos['query_filter'],
                                ([],[]))
            self.assertEqual(   qinfos['target_class'],
                                tclass)

class LeFilteredQueryTestCase(unittest.TestCase):

    q_classes = [ LeDeleteQuery, LeUpdateQuery, LeGetQuery ]

    def test_filters(self):
        """ Testing FilteredQuery filters handling """
        test_datas = [  (   'lodel_id = 42',
                            (   [('lodel_id','=','42')],
                                [])),
                        (   'lodel_id <= 42',
                            (   [('lodel_id','<=','42')],
                                [])),
                        (   ['lodel_id <= 42'],
                            (   [('lodel_id','<=','42')],
                                [])),
                        (   ('lodel_id <= 42',),
                            (   [('lodel_id','<=','42')],
                                [])),
                        (   ['lodel_id <= 42','lodel_id >= 33'],
                            (   [   ('lodel_id','<=','42'),
                                    ('lodel_id', '>=','33')],
                                [])),
        ]
        for q_class in self.q_classes:
            for q_filter_arg, e_qfilter in test_datas:
                get_q = q_class(dyncode.Publication, q_filter_arg)
                self.assertEqual(   get_q.dump_infos()['query_filter'],
                                    e_qfilter)

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
                with self.assertRaises( LeApiDataCheckError,
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
        values = (  '42',
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
