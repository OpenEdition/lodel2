import unittest

from lodel.leapi.datahandlers.datas import Concat, Varchar
from lodel.editorial_model.components import EmClass
from lodel.leapi.datahandlers.base_classes import DatasConstructor

class ConcatTestCase(unittest.TestCase):

    # @TODO use Data Constructors
    def test_construct_data(self):
        test_class = EmClass('testing', display_name='testing class')
        test_class.new_field('field1', 'varchar')
        test_class.new_field('field2', 'varchar')

        datas = {'field1': 'o'*5, 'field2': 'k'*4}
        datas2 = {'field1': 'o'*5, 'field2': 'k'*10}

        test_concat = Concat(['field1', 'field2'], '*')
        concat_string_value = test_concat.construct_data(test_class, 'field', datas, '')
        self.assertEqual('%s*%s' % ('o'*5, 'k'*4), concat_string_value)

        test_concat.max_length=10
        concat_string_value = test_concat.construct_data(test_class, 'field', datas2, '')
        test_value = '%s*%s' % ('o'*5, 'k'*10)
        self.assertNotEqual(test_value, concat_string_value)
        self.assertEqual(len(concat_string_value), test_concat.max_length)
        self.assertTrue(concat_string_value in test_value)