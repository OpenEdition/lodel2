#-*- coding: utf-8 -*-

import copy
import unittest
from unittest import mock
from unittest.mock import patch, call, Mock

import leapi.test.utils
from Lodel.hooks import LodelHook

class LodelHookTestCase(unittest.TestCase):

    #Dynamic code generation & import
    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()

    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leapi.test.utils.cleanup(cls.tmpdir)

    def test_hook_registration(self):
        """ Testing hooks registration """
        self.assertEqual(LodelHook.hook_list('test_hook'), dict())
        @LodelHook('test_hook', 42)
        def test_hook(hook_name, caller, payload):
            pass
        @LodelHook('test_hook', 1)
        def test2_hook(hook_name, caller, payload):
            pass
        @LodelHook('test_hook')
        def test3_hook(hook_name, caller, payload):
            pass

        self.assertEqual(   LodelHook.hook_list('test_hook'),
                            {
                                'test_hook':[
                                    (test2_hook, 1),
                                    (test_hook, 42),
                                    (test3_hook, 0xFFFF),
                                ]
                            }
        )

    def test_hook_call(self):
        """ Testing hooks call """
        # Registering a mock as hook
        mockhook = Mock()
        decorator = LodelHook('test_hook_call')
        decorator(mockhook)
        
        LodelHook.call_hook('test_hook_call', leapi, [1,2,3,42])
        mockhook.assert_called_once_with('test_hook_call', leapi, [1,2,3,42])
        mockhook.reset_mock()
        LodelHook.call_hook('test_hook_call', None, 'datas')
        mockhook.assert_called_once_with('test_hook_call', None, 'datas')

    def test_leapi_get_hook_leobject(self):
        """ Testing that leapi_get_* hooks get called when calling get on LeObject """
        from dyncode import Numero, Article, Publication, Textes, LeRelation, LeObject, LeRelation
        call_args = {
                        'query_filters': [],
                        'offset': 0,
                        'limit': None,
                        'order': None,
                        'group': None,
                        'field_list': None
        }
        for leo in [Numero, Article, Publication, Textes, LeObject]:
            call_args_full = copy.copy(call_args)
            if 'instanciate' not in call_args_full:
                call_args_full['instanciate'] = True
            if leo.implements_letype():
                call_args_full['query_filters'].append( ('type_id', '=', leo._type_id) )
            if leo.implements_leclass():
                call_args_full['query_filters'].append( ('class_id', '=', leo._class_id) )

            with patch.object(LodelHook, 'call_hook', return_value=call_args_full) as callhook_mock:
                foo = leo.get(**call_args)
                expected_calls = [
                    call('leapi_get_pre', leo, call_args_full),
                    call('leapi_get_post', leo, None)
                ]
                callhook_mock.assert_has_calls(expected_calls, any_order = False)

    def test_leapi_get_hook_lerelation(self):
        """ Testing that leapi_get_* hooks get called when calling get on LeRelation """
        from dyncode import LeRelation, LeRel2Type, LeHierarch, RelTextesPersonneAuteur
        call_args = {
                        'query_filters': [],
                        'offset': 0,
                        'limit': None,
                        'order': None,
                        'group': None,
                        'field_list': None
        }
        for lerel in [LeRelation, LeRel2Type, LeHierarch, RelTextesPersonneAuteur]:
            call_args_full = copy.copy(call_args)
            if 'instanciate' not in call_args_full:
                call_args_full['instanciate'] = True

            with patch.object(LodelHook, 'call_hook', return_value=call_args_full) as callhook_mock:
                foo = lerel.get(**call_args)
                expected_calls = [
                    call('leapi_get_pre', lerel, call_args_full),
                    call('leapi_get_post', lerel, None),
                ]
                callhook_mock.assert_has_calls(expected_calls, any_order = False)
    
    def test_leapi_update_hook(self):
        """ Testing that leapi_update_* hooks get called when calling update on LeCrud child instance"""
        from leapi.lecrud import _LeCrud
        from dyncode import Numero, Publication, LeRelation, RelTextesPersonneAuteur

        call_args = {'datas':dict()}
        
        for leo in [Numero, Publication, RelTextesPersonneAuteur]:
            with patch.object(_LeCrud, 'populate', return_value = None) as osef_mock:
                with patch.object(LodelHook, 'call_hook', return_value = call_args) as callhook_mock:
                    inst = leo(42)
                    inst.update(**call_args)
                    expected_calls = [
                        call('leapi_update_pre', inst, call_args),
                        call('leapi_update_post', inst, False),
                    ]
                    callhook_mock.assert_has_calls(expected_calls, any_order = False)

    def test_leapi_delete_hooks(self):
        """ Testing that leapi_delete_* hooks get called when calling delete on LeCrud child instance"""
        from dyncode import Numero, Publication, LeRelation, RelTextesPersonneAuteur
        for leo in [Numero, Publication, RelTextesPersonneAuteur]:
            with patch.object(LodelHook, 'call_hook', return_value = None) as callhook_mock:
                inst = leo(42)
                inst.delete()
                expected_calls = [
                    call('leapi_delete_pre', inst, None),
                    call('leapi_delete_post', inst, None)
                ]
                callhook_mock.assert_has_calls(expected_calls, any_order = False)

    def test_leapi_insert_hooks(self):
        """ Testing that leapi_insert_* hooks get called when calling insert on LeCrud child instance """
        # Only testing with Article because datas check is anoying
        from dyncode import Article
        call_args = {
            'datas': {
                        'titre': 'test',
                        'soustitre': 'avec des mocks',
            }
        }

        full_args = copy.copy(call_args)
        full_args['classname'] = None

        with patch.object(LodelHook, 'call_hook', return_value = full_args) as callhook_mock:
            Article.insert(**call_args)
            expected_calls = [
                call('leapi_insert_pre', Article, full_args),
                call('leapi_insert_post', Article, None),
            ]
            callhook_mock.assert_has_calls(expected_calls)
