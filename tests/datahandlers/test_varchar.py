import unittest
from lodel.leapi.datahandlers.datas import Varchar, Integer
from lodel.leapi.datahandlers.base_classes import FieldValidationError
from lodel.exceptions import *

test_varchar = Varchar(max_length=10)
class VarcharTestCase(unittest.TestCase):

    def test_check_good_data_value(self):
        for test_value in ["c" * 10, "c" * 9]:
            value = test_varchar._check_data_value(test_value)
            self.assertEqual(value, test_value)

    def test_check_bad_data_value(self):
        for test_value in ["c" * 11]:
            with self.assertRaises(FieldValidationError):
                value = test_varchar._check_data_value(test_value)

    def test_can_override(self):
        test_varchar1 = Varchar()
        test_integer = Integer()
        test_varchar2 = Varchar()

        self.assertFalse(test_varchar1.can_override(test_integer))
        self.assertTrue(test_varchar1.can_override(test_varchar2))
