import unittest

from lodel.leapi.datahandlers.datas import FormatString
from lodel.editorial_model.components import EmClass


class FormatStringTestCase(unittest.TestCase):

    def test_construct_data(self):
        test_class = EmClass('testing',display_name='testing class')
        test_class.new_field('field1', 'varchar')
        test_class.new_field('field2', 'varchar')

        test_formatstring = FormatString('%s_%s',['field1', 'field2'], max_length=10)
        formatted_string_value = test_formatstring.construct_data(test_class, 'field', {'field1': 'o'*5, 'field2': 'k'*4}, '')
        self.assertEqual('%s_%s' % ('o'*5, 'k'*4), formatted_string_value)

    def test_construct_too_long_data(self):
        test_class = EmClass('testing', display_name='testing class')
        test_class.new_field('field1', 'varchar')
        test_class.new_field('field2', 'varchar')
        test_formatstring = FormatString('%s-%s', ['field2', 'field1'], max_length=10)
        formatted_string_value = test_formatstring.construct_data(test_class, 'field', {'field1': 'o'*300, 'field2': 'k'*500},'')
        test_value = '%s-%s' % ('k'*500, 'o'*300)
        self.assertNotEqual(test_value, formatted_string_value)
        self.assertTrue(formatted_string_value in test_value)
        self.assertTrue(len(formatted_string_value) == test_formatstring.max_length)
        self.assertEqual(formatted_string_value, test_value[:test_formatstring.max_length])