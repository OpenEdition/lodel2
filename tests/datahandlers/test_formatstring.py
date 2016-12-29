import unittest

from lodel.leapi.datahandlers.datas import FormatString
from lodel.editorial_model.components import EmClass

class FormatStringTestCase(unittest.TestCase):

        
    def test_base_type_is_char(self):
        self.assertEqual(FormatString.base_type, 'char')
        
        
    def test_help_property_str_is_set(self):
        self.assertEqual(type(FormatString.help), str)


    def test_string_formatting_output(self):
        testee = FormatString(self.regex,[self.fone_name, self.ftwo_name])
        
        expected_result = self.regex % (self.field_one_value, self.field_two_value)
        actual_result = testee.construct_data(self.dummyEmClass, None, self.field_value_dict, None)

        self.assertEqual(actual_result, expected_result)
        
        
    def test_throws_user_warning_on_exceeding_string(self):
        max_length = len(self.regex % (self.field_one_value, self.field_two_value)) / 2
        testee = FormatString(self.regex, self.field_list, max_length=self.max_length)
        
        self.assertWarns(
            UserWarning,
            testee.construct_data,
            self.dummyEmClass, None, self.field_value_dict, None
        )
            
            
    def test_exceeding_string_length_is_truncated(self):
        max_length = 2
        testee = FormatString(self.regex, self.field_list, max_length=self.max_length)
        result_string = testee._construct_data(self.dummyEmClass, None, self.field_value_dict, None)
        
        self.assertEqual(self.max_length, len(result_string))
        
            
    def test_thrown_exceeding_str_warning_message_composition(self):
        testee = FormatString(self.regex, self.field_list, max_length=self.max_length)
        
        self.assertWarnsRegex(
            UserWarning,
            '[T|t]runcat[a-z]+',
            testee.construct_data,
            self.dummyEmClass, None, self.field_value_dict, None
        )
            
    
    def setUp(self):
        self.regex = '%s-%s'
        self.dummyEmClass = EmClass('testing')
        self.fone_name = 'field1'
        self.ftwo_name = 'field2'
        self.dummyEmClass.new_field(self.fone_name, 'varchar')
        self.dummyEmClass.new_field(self.ftwo_name, 'varchar')
        self.field_one_value = 'field one value'
        self.field_two_value = 'field two value'
        self.field_value_dict = {self.fone_name: self.field_one_value, self.ftwo_name: self.field_two_value}
        self.field_list = [self.fone_name, self.ftwo_name]
        
        self.max_length = round(len(self.regex % (self.field_one_value, self.field_two_value)) / 2)
        