import unittest

from lodel.leapi.datahandlers.datas import DateTime


class DatetimeTestCase(unittest.TestCase):

    def test_datetime_check_data_value(self):
        test_datetime = DateTime()

        test_value = '2016-01-01'
        _, error = test_datetime.check_data_value(test_value)
        self.assertIsNone(error)

    def test_datetime_check_data_value_with_custom_format(self):
        test_value = '2016-01-01T10:20:30Z'
        test_datetime = DateTime(format='%Y-%m-%dT%H:%M:%SZ')
        _, error = test_datetime.check_data_value(test_value)
        self.assertIsNone(error)

    def test_check_bad_value(self):
        test_datetime = DateTime(now_on_create=True, now_on_update=True)
        test_value = '2016-01-01-test'
        _, error = test_datetime.check_data_value(test_value)
        self.assertIsNotNone(error)
