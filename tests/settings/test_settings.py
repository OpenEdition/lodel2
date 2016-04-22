#-*- coding: utf-8 -*-

import unittest
from unittest import mock

import tests.loader_utils
from lodel.settings.settings import Settings
from lodel.settings.settings import SettingsLoader

def dummy_validator(value): return value

class SettingsTestCase(unittest.TestCase):
    
    def test_init(self):
        with self.assertRaises(RuntimeError):
            Settings('tests/settings/settings_tests_conf.d')
        
    def test_set(self):
        loader = SettingsLoader('globconf.d')
        Settings.set('lodel2.editorialmodel.emfile','test ok', dummy_validator, loader)
        Settings.set('lodel2.editorialmodel.editormode','test ok', dummy_validator, loader)
        loader = SettingsLoader('globconf.d')
        option = loader.getoption('lodel2.editorialmodel','emfile', dummy_validator)
        self.assertEqual(option , 'test ok')
        option = loader.getoption('lodel2.editorialmodel','editormode', dummy_validator)
        self.assertEqual(option, 'test ok')
        Settings.set('lodel2.editorialmodel.emfile','examples/em_test.pickle', dummy_validator, loader)
        Settings.set('lodel2.editorialmodel.editormode','True', dummy_validator, loader)

