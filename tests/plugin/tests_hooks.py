#-*- coding: utf-8 -*-

import unittest
from unittest.mock import MagicMock

from lodel.plugin.plugins import Plugin, PluginError
from lodel.plugin.hooks import LodelHook

testhook = 'are_we_sure_that_this_name_is_uniq'

class HookTestCase(unittest.TestCase):

    def setUp(self):
        LodelHook.__reset__()

    def test_registration(self):
        """ Testing hook registration using decorator (checking using hook_list() """
        hook_list = LodelHook.hook_list(testhook)
        self.assertEqual({}, hook_list)
        #hook_registration
        @LodelHook(testhook,42)
        def funny_fun_test_hook(hook_name, caller, payload):
            pass
        hook_list = LodelHook.hook_list(testhook)
        self.assertEqual({testhook: [(funny_fun_test_hook, 42)]}, hook_list)

    def test_call(self):
        """ Testing LodelHook.call_hook() """
        #manual registration using a mock
        mmock = MagicMock(return_value = '4242')
        mmock.__name__ = 'mmock'
        hooking = LodelHook(testhook, 1337)
        hooking(mmock)
        res = LodelHook.call_hook(testhook, 'Caller', 'payload')
        #Check returned value
        self.assertEqual(
            res,
            '4242',
            'Expected value was "4242" but found %s' % res)
        #Checks call
        mmock.assert_called_once_with(testhook, 'Caller', 'payload')


