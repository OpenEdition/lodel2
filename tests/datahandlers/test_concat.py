import unittest

from lodel.leapi.datahandlers.data import Concat as Testee


class ConcatTestCase(unittest.TestCase):
    
    
    def test_base_type_is_char(self):
        self.assertEqual(Testee.base_type, 'char')
        
        
    def test_help_property_str_is_set(self):
        self.assertEqual(type(Testee.help), str)
        
    
    def test_correctly_sets_format_string(self):
        separator = '-'
        field_list  = ['', '', '']
        testee = Testee(field_list, separator)
        
        self.assertEqual(testee._format_string, separator.join(['%s' for _ in field_list]))