import unittest
from lodel.exceptions import *

from lodel.leapi.datahandlers.data import Boolean, Varchar, Integer


test_boolean = Boolean()
class BooleanTestCase(unittest.TestCase): 

    def test_boolean_good_check_data_value(self):
        for test_value in [True, False]:
            value = test_boolean._check_data_value(test_value)
            self.assertEqual(value, bool(test_value))

    def test_boolean_bad_check_data_value(self):
        for test_value in ['ok', 'True', 'False']:
            with self.assertRaises(FieldValidationError):
                test_boolean._check_data_value(test_value)

    def test_can_override(self):

        test_varchar = Varchar()
        test_int = Integer()

        self.assertFalse(test_boolean.can_override(test_varchar))
        self.assertFalse(test_boolean.can_override(test_int))
