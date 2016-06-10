import unittest

import itertools

import tests.loader_utils
from tests.leapi.query.utils import dyncode_module as dyncode

from lodel.leapi.query import LeDeleteQuery, LeUpdateQuery, LeGetQuery
from lodel.leapi.exceptions import LeApiQueryError

class LeGetQueryTestCase(unittest.TestCase):
    
    def test_init_default(self):
        """ Testing GetQuery instanciation arguments default value """
        tclass_list = [ dyncode.Object,
                        dyncode.Entry,
                        dyncode.Person,
                        dyncode.Text,
                        dyncode.Section,
                        dyncode.Publication,
                        dyncode.Text_Person ]

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

    def test_field_list(self):
        """ Testing GetQuery field list argument processing """
        tclass_list = [ dyncode.Object,
                        dyncode.Entry,
                        dyncode.Person,
                        dyncode.Text,
                        dyncode.Section,
                        dyncode.Publication,
                        dyncode.Text_Person ]
        
        for tclass in tclass_list:
            # testing all field list possible combinations
            field_list = tclass.fieldnames(True)
            for r in range(1, len(field_list) + 1):
                combinations = [ list(c) for c in itertools.combinations(field_list, r)]
                for test_flist in combinations:
                    expected = set(test_flist)
                    get_q = LeGetQuery(tclass, [], field_list = test_flist)
                    qinfos = get_q.dump_infos()
                    self.assertEqual(   sorted(qinfos['field_list']),
                                        sorted(test_flist))
                
    def test_field_list_duplicated(self):
        """ Testing GetQuery field list argument deduplication """
        tclass_list = [ dyncode.Object,
                        dyncode.Text,
                        dyncode.Section,
                        dyncode.Publication,
                        dyncode.Text_Person ]
        for tclass in tclass_list:
            fl = [  'lodel_id',
                    'lodel_id',
                    'help_text',
                    'help_text',
                    'help_text']
            get_q = LeGetQuery(tclass, [], field_list = fl)
            self.assertEqual(   sorted(list(set(fl))),
                                sorted(get_q.dump_infos()['field_list']))

    def test_field_list_invalid(self):
        """ Testing GetQuery invalid field name detection in field list """
        bad_field_lists = ( ('non-existing',),
                            (1,),
                            (True,),
                            (None,),
                            ('lodel_id', 'non-existing',),
                            ('lodel_id', 1,),
                            ('lodel_id', True,),
                            ('lodel_id', None,) )

        for bad_field_list in bad_field_lists:
            with self.assertRaises(LeApiQueryError):
                LeGetQuery(dyncode.Object, [], field_list = bad_field_list)

