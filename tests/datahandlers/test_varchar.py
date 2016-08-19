import unittest

from lodel.leapi.datahandlers.datas import Varchar, Integer


class VarcharTestCase(unittest.TestCase):

    def test_check_data_value(self):
        test_varchar = Varchar(max_length=10)

        _, error = test_varchar.check_data_value("c" * 10)
        self.assertIsNone(error)

        _, error = test_varchar.check_data_value("c" * 9)
        self.assertIsNone(error)

        _, error = test_varchar.check_data_value("c" * 11)
        self.assertIsNotNone(error)
        self.assertIsInstance(error, ValueError)

    def test_can_override(self):
        test_varchar1 = Varchar()
        test_integer = Integer()
        test_varchar2 = Varchar()

        self.assertFalse(test_varchar1.can_override(test_integer))
        self.assertTrue(test_varchar1.can_override(test_varchar2))