#-*- coding: utf-8 -*-

import unittest

from lodel.plugin.plugins import Plugin, PluginError
from lodel.settings.settings import Settings
import tests.loader_utils

class PluginTestCase(unittest.TestCase):

    def test_plugin_init_right_name(self):
        Plugin.start(['/home/helene/lodel2/plugins'],['dummy'])
        Plugin.clear()
        
    # With a wrong plugin name, a NameError Exception has to be raised at line 318 of plugin.py
    def test_plugin_init_wrong_name(self):
        with self.assertRaises(NameError):
            Plugin.start(['/home/helene/lodel2/plugins', '/home/helene/lodel2/tests/tests_plugins' ],['wrong_plugin_name'])
        Plugin.clear()
        
    # With a wrong plugin name, a NameError Exception has to be raised at line 318 of plugin.py
    def test_plugin_init_right_wrong_name(self):
        with self.assertRaises(NameError):
            Plugin.start(['/home/helene/lodel2/plugins', '/home/helene/lodel2/tests/tests_plugins'],['dummy', 'wrong_plugin_name'])
        Plugin.clear()
    
    def test_plugin_started(self):
        with self.assertRaises(RuntimeError):
            Plugin.started()
            
    def test_plugin_plugin_path(self):
        Plugin.start(['/home/helene/lodel2/plugins', '/home/helene/lodel2/tests/tests_plugins'],['dummy'])
        self.assertEqual(Plugin.plugin_path('dummy'), '/home/helene/lodel2/plugins/dummy/')
        Plugin.clear()
        
    def test_plugin_get(self):
        Plugin.start(['/home/helene/lodel2/plugins', '/home/helene/lodel2/tests/tests_plugins'],['dummy'])
        with self.assertRaises(PluginError):
            Plugin.get('wrong_plugin_name')
        self.assertTrue(isinstance(Plugin.get('dummy'), Plugin))
        Plugin.clear()
        
    def test_plugin_register(self):
        with self.assertRaises(RuntimeError):
            Plugin.register('dummy')
        Plugin.start(['/home/helene/lodel2/plugins'],['dummy'])
        with self.assertRaises(PluginError):
            Plugin.register('dummy')
        Plugin.clear()
        
    def test_plugin_load_all(self):
        #Plugin.start(['/home/helene/lodel2/plugins'],['dummynotactivable'])
        #Plugin.load_all()
        pass
        
    
     
        
        
        
        
        
        
        
