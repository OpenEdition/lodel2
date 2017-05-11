import unittest
from lodel.leapi.datahandlers.data import Password as Testee


class PasswordTestCase(unittest.TestCase):
        
        
    def test_base_type_property_value_equals_password(self):
        self.assertEqual(Testee.base_type, 'password')
        
        
    def test_help_property_string_is_set(self):
        self.assertEqual(type(Testee.help), str)