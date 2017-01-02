import unittest

from lodel.leapi.datahandlers.datas import Text
from lodel.exceptions import FieldValidationError


class TextTestCase(unittest.TestCase):
    
    
    def test_base_type_property_value_equals_text(self):
        self.assertEqual(Text.base_type, 'text')


    def test_non_string_value_throws_FieldValidationError(self):
        self.assertRaises(
            FieldValidationError,
            Text()._check_data_value,
            bool
            )
    

    def test_check_data_returns_unchanged_strnig_parameter_if_valid(self):
        test_value = """ Ceci est un texte multiligne pour tester le check
        sur le datahandler
        Text
        """
        self.assertEqual(Text()._check_data_value(test_value), test_value)
