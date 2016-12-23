import unittest

from lodel.leapi.datahandlers.datas import FormatString as Testee
from lodel.editorial_model.components import EmClass

class TesteeTestCase(unittest.TestCase):
    regex = '%s-%s'
    dummyEmClass = EmClass('testing')
    fone_name = 'field1'
    ftwo_name = 'field2'
    dummyEmClass.new_field(fone_name, 'varchar')
    dummyEmClass.new_field(ftwo_name, 'varchar')
    field_one_value = 'field one value'
    field_two_value = 'field two value'
    field_value_dict = {fone_name: field_one_value, ftwo_name: field_two_value}
    field_list = [fone_name, ftwo_name]
    
    test_Testee = Testee(regex,[fone_name, ftwo_name])
    
    max_length = round(len(regex % (field_one_value, field_two_value)) / 2)


    def test_has_base_type_property(self):
        self.assertTrue(hasattr(Testee, 'base_type'))
        
        
    def test_base_type_is_char(self):
        self.assertEqual(Testee.base_type, 'char')
        
        
    def test_has_help_property(self):
        self.assertTrue(hasattr(Testee, 'help'))
        
        
    def test_help_property_str_is_set(self):
        self.assertEqual(type(Testee.help), str)


    def test_string_formatting_output(self):
        expected_result = self.regex % (self.field_one_value, self.field_two_value)
        actual_result = self.test_Testee.construct_data(self.dummyEmClass, None, self.field_value_dict, None)

        self.assertEqual(actual_result, expected_result)
        
        
    def test_throws_user_warning_on_exceeding_string(self):
        max_length = len(self.regex % (self.field_one_value, self.field_two_value)) / 2
        testee = Testee(self.regex, self.field_list, max_length=self.max_length)
        
        with self.assertWarns(UserWarning):
            testee.construct_data(self.dummyEmClass, None, self.field_value_dict, None)
            
            
    def test_exceeding_string_length_is_truncated(self):
        max_length = 2
        testee = Testee(self.regex, self.field_list, max_length=self.max_length)
        result_string = testee._construct_data(self.dummyEmClass, None, self.field_value_dict, None)
        
        self.assertEqual(self.max_length, len(result_string))
        
            
    def test_thrown_exceeding_str_warning_message_composition(self):
        testee = Testee(self.regex, self.field_list, max_length=self.max_length)
        
        with self.assertWarnsRegex(UserWarning, '[T|t]runcat[a-z]+'):
            testee.construct_data(self.dummyEmClass, None, self.field_value_dict, None)