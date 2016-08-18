import unittest

from lodel.leapi.datahandlers.datas import Integer, Boolean


class IntegerTestCase(unittest.TestCase):

    def test_integer_check_data_value(self):
        test_int = Integer()

        # Incorrect values
        for test_bad_value in ['ok','ceci est un test', '15.2', 15.2]:
            _, error = test_int._check_data_value(test_bad_value)
            self.assertIsNotNone(error)
            print(test_bad_value)

        # Correct values
        for test_correct_value in [10, '15', '15.0']:
            _, error = test_int._check_data_value(test_correct_value)
            self.assertIsNone(error)
            print(test_correct_value)

    def test_can_override(self):
        test_int = Integer()
        test_boolean = Boolean()
        self.assertFalse(test_int.can_override(test_boolean))