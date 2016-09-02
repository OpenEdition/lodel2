#-*- coding: utf-8 -*-

import unittest

from lodel.plugin.plugins import Plugin, PluginError
from lodel.plugin.datasource_plugin import DatasourcePlugin
from lodel.plugin.sessionhandler import SessionHandlerPlugin
from lodel.plugin.interface import InterfacePlugin
from lodel.plugin.extensions import Extension
from lodel.settings.settings import Settings
import tests.loader_utils

##@todo write tests about discovering
class PluginTestCase(unittest.TestCase):
    """ Test case grouping all tests on Plugin class init procedures """

    def setUp(self):
        Plugin.clear()

    def test_start(self):
        """ Testing plugin registration with a valid list of plugins name """
        Plugin.start(['dummy', 'dummy_datasource'])

    def test_double_start(self):
        """ Testing clas behavior when starting it twice """
        Plugin.start(['dummy', 'dummy_datasource'])
        with self.assertRaises(PluginError):
            Plugin.start(['dummy', 'dummy_datasource'])

    def test_clear(self):
        """ Testing that clear allow to start again Plugin """
        Plugin.start(['dummy', 'dummy_datasource'])
        Plugin.clear()
        Plugin.start(['dummy', 'dummy_datasource'])

class PluginStartedTestCase(unittest.TestCase):
    """ Test case grouping all tests on a started Plugin class """

    @classmethod
    def setUpClass(cls):
        Plugin.clear()
        Plugin.start(['dummy', 'dummy_datasource', 'webui', 'ram_session'])

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
