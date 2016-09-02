import unittest

from lodel.leapi.datahandlers.datas import Regex, Varchar, Integer


class RegexTestCase(unittest.TestCase):

    def test_check_correct_data_value(self):
        test_value = '126.205.255.12'
        test_regex = Regex('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                           max_length=100)
        value, error = test_regex.check_data_value(test_value)
        self.assertIsNone(error)
        self.assertEqual(value, test_value)

    def test_check_bad_data_value(self):
        test_regex = Regex('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                           max_length=15)
        for test_value in ['800.9.10.5', 'test_string_value', '999.999.999.999']:
            value, error = test_regex.check_data_value(test_value)
            self.assertEqual(value, None)
            self.assertIsNotNone(error)

    def test_check_max_length(self):
        test_max_length = 15
        test_regex = Regex('[a-z]+8?', max_length=15)
        for test_value in ['cccccc8', 'ccccccccccccccccccccccccccccccccc8']:
            value, error = test_regex.check_data_value(test_value)
            if len(test_value)>test_max_length:
                self.assertEqual(value, None)
                self.assertIsNotNone(error)
            else:
                self.assertIsNone(error)
                self.assertEqual(value, test_value)

    def test_can_override(self):
        test_regex = Regex('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                           max_length=15)
        for test_varchar in [Varchar(), Varchar(max_length=15), Varchar(max_length=9)]:
            if test_regex.max_length == test_varchar.max_length:
                self.assertTrue(test_regex.can_override(test_varchar))
            else:
                self.assertFalse(test_regex.can_override(test_varchar))

    def test_cant_override(self):
        test_regex = Regex('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                           max_length=15)
        test_int = Integer()
        self.assertFalse(test_regex.can_override(test_int))
