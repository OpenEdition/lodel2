import unittest

from lodel.leapi.datahandlers.base_classes import DataHandler
from lodel.leapi.datahandlers.datas import Varchar


class DataHandlerTestCase(unittest.TestCase):

    def test_init_abstract_class(self):
        datahandler = None
        try:
            datahandler = DataHandler()
        except NotImplementedError:
            self.assertNotIsInstance(datahandler, DataHandler)
            self.assertIsNone(datahandler)

    def test_register_new_handler(self):
        DataHandler.register_new_handler('testvarchar', Varchar)
        self.assertEqual(DataHandler.from_name('testvarchar'), Varchar)

    def test_register_nonclass_as_handler(self):
        try:
            DataHandler.register_new_handler('testvarchar', 'common string')
        except Exception as err:
            self.assertEqual(ValueError, type(err))

    def test_register_invalid_class_as_handler(self):

        try:
            DataHandler.register_new_handler('testvarchar', Exception)
        except Exception as err:
            self.assertEqual(ValueError, type(err))

    def test_from_name(self):
        DataHandler.register_new_handler('test_varchar', Varchar)
        self.assertEqual(DataHandler.from_name('test_varchar'), Varchar)

