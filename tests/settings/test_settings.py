#-*- coding: utf-8 -*-

import unittest
from unittest import mock

from lodel.settings.settings import Settings

class SettingsTestCase(unittest.TestCase):
    
    def test_init(self):
        settings = Settings('tests/settings/settings_tests.ini', 'tests/settings/settings_tests_conf.d')
        print(settings.confs)
        pass
