# 
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import unittest

from lodel.plugin.plugins import Plugin, PluginError, MetaPlugType,\
    VIRTUAL_PACKAGE_NAME, PLUGINS_PATH
from lodel.plugin.datasource_plugin import DatasourcePlugin
from lodel.plugin.sessionhandler import SessionHandlerPlugin
from lodel.plugin.interface import InterfacePlugin
from lodel.plugin.extensions import Extension
from lodel.settings.settings import Settings
import tests.loader_utils

from unittest.mock import patch

##@todo write tests about discovering
##@todo finish tests for plugin_path
##@todo finish tests for check_deps
##@todo write tests for loader_module
##@todo write tests for load_all (ran upon problems as "dummy_datasource"
##      already is "pre-loaded" (I guess), but cannot be found in
##      _plugin_instances (without doing some other work before, I guess)
class PluginTestCase(unittest.TestCase):

    def setUp(self):
        Plugin.clear()
        self.working_plugins_list = ['dummy', 'dummy_datasource']
    
    
    def test_check_deps_returns_empty_list_if_no_dependencies(self):
        self.assertEqual(list(), Plugin('dummy').check_deps())    
    
    
    def test_loader_module_if_plugin_not_yet_loaded_throws_RuntimeError(self):
        self.assertRaises(RuntimeError, Plugin('dummy').loader_module)
    

    def test_start_calls_register_for_each_plugins_from_array(self):
        plugin_class = Plugin
        with patch.object(Plugin, 'register', wraps=plugin_class.register) as register_wrap:
            Plugin.start(self.working_plugins_list)
            self.assertEqual(len(self.working_plugins_list), register_wrap.call_count)


    def test_clear_effectively_allow_fresh_new_plugin_reloading(self):
        Plugin.start(self.working_plugins_list)
        Plugin.clear()
        Plugin.start(self.working_plugins_list)
        
        
    def test_register_if_plugin_already_registered_throws_PluginError(self):
        Plugin.register('dummy')
        self.assertRaises(PluginError, Plugin.register, 'dummy')
    
    
    def test_register_if_plugin_name_not_in_cache_throws_PluginError(self):
        self.assertRaises(PluginError, Plugin.register, 'azerty')
    
    
    def test_register_if_ptype_not_known_throws_PluginError(self):
        with patch.object(MetaPlugType, 'all_ptype_names', return_value=[]) as mock_method:
            self.assertRaises(PluginError, Plugin.register, 'dummy')
    
        
    def test_register_returns_Plugin_child_object(self):
        self.assertTrue(issubclass(Plugin.register('dummy_datasource').__class__, Plugin))
        
        
    def test_get_if_no_plugin_found_throws_KeyError(self):
        self.assertRaises(PluginError, Plugin.get, 'foo')
        
        
    def test_get_returns_proper_plugin_instance(self):
        Plugin.register('dummy')
        self.assertTrue(Plugin.get('dummy').__class__, Plugin)
        
    
    def test_plugin_path_if_no_plugin_name_found_throws_PluginError(self):
        self.assertRaises(PluginError, Plugin.plugin_path, 'foo')
    
    
    def test_plugin_module_name_correctly_returns_module_name_string_from_plugin_name(self):
        self.assertEqual(Plugin.plugin_module_name('foo'), "%s.%s" % (VIRTUAL_PACKAGE_NAME, 'foo'))
        
        
class PluginStartedTestCase(unittest.TestCase):
    """ Test case grouping all tests on a started Plugin class """

    @classmethod
    def setUpClass(cls):
        Plugin.clear()
        Plugin.start(['dummy', 'dummy_datasource', 'webui', 'ram_sessions'])

    @classmethod
    def tearDownClass(cls):
        Plugin.clear()

    def test_construct(self):
        """ Testing plugin instanciation """
        pname_type = {
            'dummy': Extension,
            'dummy_datasource': DatasourcePlugin,
            #'webui': InterfacePlugin, #singleton, cannot reinstanciate
            #'ram_session': SessionHandlerPlugin, #singleton, cannot resintanciate
            }
        for pname, ptype in pname_type.items():
            pinstance = Plugin.get(pname)
            self.assertIsInstance(pinstance, ptype, "Expected plugin '%s' \
to be in an %s instance but found an %s instance" % (
                pname, ptype, pinstance.__class__))

    def test_construct_invalid(self):
        """ Testing plugin instanciation with a non existing name """
        with self.assertRaises(PluginError):
            Plugin.get("fljkhsfh")
