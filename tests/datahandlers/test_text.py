import unittest

from lodel.leapi.datahandlers.datas import Text


class TextTestCase(unittest.TestCase):

    def test_check_data(self):
        test_value = """ Ceci est un texte multiligne pour tester le check
        sur le datahandler
        Text
        """
        test_text = Text()
        _, error = test_text.check_data_value(test_value)
        self.assertIsNone(error)
