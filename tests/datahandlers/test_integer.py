import unittest

from lodel.leapi.datahandlers.datas import Integer, Boolean

from lodel.exceptions import *

test_int = Integer()

class IntegerTestCase(unittest.TestCase):
    
    def test_integer_check_bad_data_value(self):
        # Incorrect values
        for test_bad_value in ['ok','ceci est un test', '15.2']:
            with self.assertRaises(FieldValidationError):
                test_int._check_data_value(test_bad_value)

    def test_integer_check_good_data_value(self):
        # Correct values
        for test_correct_value in [10, '15', 15.0, '-15.0']:
            value = test_int._check_data_value(test_correct_value)
            self.assertEqual(value, int(float(test_correct_value)))

    def test_integer_check_bad_strict_data_value(self):
        # Incorrect values
        for test_correct_value in ['15', 15.0, '15.0']:
            with self.assertRaises(FieldValidationError):
                test_int._check_data_value(test_correct_value, True)
    
    def test_integer_check_good_strict_data_value(self):
        # Correct values
        for test_correct_value in [0, 15, -15]:
            value = test_int._check_data_value(test_correct_value)
            self.assertEqual(value, int(float(test_correct_value)))
    
    def test_can_override(self):
        test_boolean = Boolean()
        self.assertFalse(test_int.can_override(test_boolean))
