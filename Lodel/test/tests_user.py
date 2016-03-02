#-*- coding: utf-8 -*-

import unittest
import unittest.mock
from unittest.mock import Mock

from Lodel.user import  authentication_method, identification_method, UserIdentity, UserContext


class AuthIdMethodTestCase(unittest.TestCase):
    
    def test_authentication_method_registration(self):
        before = set(authentication_method.list_methods())

        def test_method(self):
            pass
        authentication_method(test_method) # faking test_method decoration

        after = set(authentication_method.list_methods())
        self.assertEqual(after - before, set([test_method]))

    def test_identification_method_registration(self):
        before = set(identification_method.list_methods())

        def test_method(self):
            pass
        identification_method(test_method) # faking test_method decoration
        
        after = set(identification_method.list_methods())
        self.assertEqual(after - before, set([test_method]))

    def test_authentication_method_calls(self):
        mock_list = list()
        for i in range(5):
            auth_mock = Mock(return_value = False)
            mock_list.append(auth_mock)
            authentication_method(auth_mock)
        ret = authentication_method.authenticate('login', 'password')
        self.assertFalse(ret)
        for mock in mock_list:
            mock.assert_called_once_with('login', 'password')
        # Adding a mock that will fake a successfull auth
        user_id = UserIdentity(42, 'superlogin', authenticated = True)
        authentication_method( Mock(return_value = user_id) )
        ret = authentication_method.authenticate('login', 'password')
        self.assertEqual(ret, user_id)

    def test_identificatio_method_calls(self):
        mock_list = list()
        for i in range(5):
            id_mock = Mock(return_value = False)
            mock_list.append(id_mock)
            identification_method(id_mock)
        client_infos = {'ip':'127.0.0.1', 'user-agent': 'bla bla'}
        ret = identification_method.identify(client_infos)
        self.assertFalse(ret)
        for mock in mock_list:
            mock.assert_called_once_with(client_infos)
        # Adding a mock that will fake a successfull identification
        user_id = UserIdentity(42, 'login', identified = True)
        identification_method( Mock(return_value = user_id) )
        ret = identification_method.identify(client_infos)
        self.assertEqual(ret, user_id)

class UserIdentityTestCase(unittest.TestCase):
    
    def test_init(self):
        """ Testing UserIdentity constructor """
        uid = UserIdentity(42, 'login', 'anonymous login')
        self.assertEqual(uid.user_id, 42)
        self.assertEqual(uid.username, 'login')
        self.assertEqual(uid.fullname, 'anonymous login')
        self.assertFalse(uid.is_authenticated)
        self.assertFalse(uid.is_identified)
        self.assertEqual(str(uid), uid.fullname)

    def test_identified(self):
        """ Testing identified flag relation with authenticated flag """
        uid = UserIdentity(42, 'login', identified = True)
        self.assertTrue(uid.is_identified)
        self.assertFalse(uid.is_authenticated)

    def test_authentified(self):
        """ Testing identified flag relation with authenticated flag """
        uid = UserIdentity(42, 'login', authenticated = True)
        self.assertTrue(uid.is_identified)
        self.assertTrue(uid.is_authenticated)

    def test_anonymous(self):
        """ Testing the anonymous UserIdentity """
        anon = UserIdentity.anonymous()
        self.assertEqual(anon, UserIdentity.anonymous())
        self.assertFalse(anon.is_authenticated)
        self.assertFalse(anon.is_identified)

class UserContextTestCase(unittest.TestCase):

    '''
    def test_static(self):
        """ Testing that the class is static """
        with self.assertRaises(NotImplementedError):
            UserContext()
    '''

    '''
    def test_not_init(self):
        """ Testing method call with a non initialised class """
        UserContext.__reset__()
        with self.assertRaises(AssertionError):
            UserContext.identity()
        with self.assertRaises(AssertionError):
            UserContext.authenticate('login', 'foobar')
    '''
    def test_anon_init(self):
        """ Testing class initialisation """
        identification_method.__reset__()
        authentication_method.__reset__()
        # UserContext.__reset__()
        auth_id = UserIdentity(43, 'loggedlogin', authenticated = True)
        # Add a fake authentication method
        auth_mock = Mock(return_value = auth_id)
        authentication_method(auth_mock)
        # Are we anonymous ?
        #UserContext.init('localhost')
        user_context = UserContext('localhost')
        self.assertEqual(user_context.identity(), UserIdentity.anonymous())
        #self.assertEqual(UserContext.identity(), UserIdentity.anonymous())
        # Can we authenticate ourself ?
        #UserContext.authenticate('login', 'pass')
        user_context.authenticate('login', 'pass')
        auth_mock.assert_called_once_with('login', 'pass')
        #self.assertEqual(auth_id, UserContext.identity())
        self.assertEqual(auth_id, user_context.identity())

    def test_init(self):
        """ Testing class initialisation being identified by client_infos"""
        identification_method.__reset__()
        authentication_method.__reset__()
        # UserContext.__reset__()
        user_id = UserIdentity(42, 'login', identified = True)
        auth_id = UserIdentity(43, 'loggedlogin', authenticated = True)
        # Add a fake id method
        id_mock = Mock(return_value = user_id)
        identification_method(id_mock)
        # Add a fake authentication method
        auth_mock = Mock(return_value = auth_id)
        authentication_method(auth_mock)
        # testing lazy identification
        #UserContext.init('localhost')
        user_context = UserContext('localhost')
        id_mock.assert_not_called()
        auth_mock.assert_not_called() # should really not be called yet
        # triggering identification
        ret_id = user_context.identity()  # UserContext.identity()
        id_mock.assert_called_once_with('localhost')
        self.assertEqual(ret_id, user_id)
        auth_mock.assert_not_called() # should really not be called yet
        id_mock.reset_mock()
        # Trying to auth
        #UserContext.authenticate('identifier', 'superproof')
        user_context.authenticate('identifier', 'superproof')
        id_mock.assert_not_called()
        auth_mock.assert_called_once_with('identifier', 'superproof')
        #self.assertEqual(UserContext.identity(), auth_id)
        self.assertEqual(user_context.identity(), auth_id)
