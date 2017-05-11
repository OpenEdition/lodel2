import os
import unittest
import tempfile

from lodel.leapi.datahandlers.data import File, Varchar


class FileTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_file, cls.test_file_path = tempfile.mkstemp()

    def test_check_correct_data_value(self):

        test_file = File()

        test_value = os.path.abspath(os.path.join(os.path.curdir,'test_file.txt'))
        _, error = test_file.check_data_value(test_value)
        self.assertIsNone(error)

    @unittest.skip
    def test_check_uncorrect_data_value(self):
        test_file = File()
        test_bad_value = "invalid_path"
        _, error = test_file.check_data_value(test_bad_value)
        self.assertIsNotNone(test_bad_value)

    def test_can_override(self):
        test_file = File()

        test_file2 = File()
        self.assertTrue(test_file.can_override(test_file2))

        test_varchar = Varchar()
        self.assertFalse(test_file.can_override(test_varchar))

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.test_file_path)