import unittest
from unittest import mock 
from unittest.mock import patch

import leapi_dyncode as dyncode

from lodel.leapi.datahandlers.datas import Password as Testee


class PasswordTestCase(unittest.TestCase):
        
        
    def test_has_base_type_property(self):
        self.assertTrue(hasattr(Testee, 'base_type'))
        
        
    def test_base_type_is_password(self):
        self.assertEqual(Testee.base_type, 'password')
        
        
    def test_has_help_property(self):
        self.assertTrue(hasattr(Testee, 'help'))
        
        
    def test_help_property_str_is_set(self):
        self.assertEqual(type(Testee.help), str)