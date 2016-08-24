import unittest

from lodel.leapi.datahandlers.base_classes import DataHandler


class DataHandlerTestCase(unittest.TestCase):

    def test_init_abstract_class(self):
        datahandler = None
        try:
            datahandler = DataHandler()
        except NotImplementedError:
            self.assertNotIsInstance(datahandler, DataHandler)
            self.assertIsNone(datahandler)
    