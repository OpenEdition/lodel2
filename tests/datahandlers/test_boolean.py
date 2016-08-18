import unittest

from lodel.leapi.datahandlers.datas import Boolean


class BooleanTestCase(unittest.TestCase):

    def test_boolean_check_data_value(self):
        test_boolean = Boolean()

        # correct values
        for test_value in [True, False]:
            value, error = test_boolean._check_data_value(test_value)
            self.assertIsNone(error)

        # incorrect values
        for test_value in ['ok', 'True', 'False']:
            value, error = test_boolean._check_data_value(test_value)
            self.assertIsNotNone(error)
