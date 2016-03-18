#-*- coding: utf-8 -*-

import unittest

from lodel.editorial_model.component import EmComponent, EmClass, EmField
from lodel.utils.mlstring import MlString

class EmComponentTestCase(unittest.TestCase):
    
    def test_abstract_init(self):
        with self.assertRaises(NotImplementedError):
            EmComponent('test')

class EmClassTestCase(unittest.TestCase):

    def test_init(self):
        cls = EmClass('testClass', 'test class', 'A test class')
        self.assertEqual(cls.uid, 'testClass')
        self.assertEqual(cls.display_name, MlString('test class'))
        self.assertEqual(cls.help_text, MlString('A test class'))
