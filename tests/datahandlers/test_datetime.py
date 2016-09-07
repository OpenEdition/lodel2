import unittest
import datetime
from lodel.leapi.datahandlers.datas import DateTime
from lodel.exceptions import *


class DatetimeTestCase(unittest.TestCase):

    def test_datetime_check_data_value(self):
        test_datetime = DateTime()
        for test_value in ['2016-01-01']:
            value = test_datetime._check_data_value(test_value)
            self.assertEqual(value, datetime.datetime(2016, 1, 1, 0, 0))

    def test_datetime_check_data_value_with_custom_format(self):
        test_value = '2016-01-01T10:20:30Z'
        test_datetime = DateTime(format='%Y-%m-%dT%H:%M:%SZ')
        value = test_datetime._check_data_value(test_value)
        self.assertEqual(value, datetime.datetime(2016, 1, 1, 10, 20, 30))

    def test_check_bad_value(self):
        test_datetime = DateTime(now_on_create=True, now_on_update=True)
        for test_value in ['2016-01-01-test', '2016/01/01', 2016]:
            with self.assertRaises(FieldValidationError):
                test_datetime._check_data_value(test_value)
