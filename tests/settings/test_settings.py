#-*- coding: utf-8 -*-

import unittest
from unittest import mock

import tests.loader_utils
from lodel.settings.settings import Settings
from lodel.settings.settings import SettingsLoader
from lodel.settings.utils import SettingsError, SettingsErrors

def dummy_validator(value): return value

class SettingsTestCase(unittest.TestCase):
    
    def test_init(self):
        with self.assertRaises(RuntimeError):
            Settings('conf.d')
    
    #@unittest.skip("This tests doesn't pass anymore, but I do not understand why it should pass")
    def test_set(self):

        Settings.set('lodel2.editorialmodel.emfile','test ok', dummy_validator)
        Settings.set('lodel2.editorialmodel.editormode','test ok', dummy_validator)
        loader = SettingsLoader('conf.d')
        option = loader.getoption('lodel2.editorialmodel','emfile', dummy_validator)
        option = loader.getoption('lodel2.editorialmodel','editormode', dummy_validator)
        self.assertEqual(option , 'test ok')
        option = loader.getoption('lodel2.editorialmodel','editormode', dummy_validator)
        self.assertEqual(option, 'test ok')
        Settings.set('lodel2.editorialmodel.emfile','examples/em_test.pickle', dummy_validator)
        Settings.set('lodel2.editorialmodel.editormode','True', dummy_validator)
        
