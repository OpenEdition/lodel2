#-*- coding: utf-8 -*-

import unittest
from unittest import mock
from unittest.mock import patch

from lodel.exceptions import *
from lodel.settings.validator import *

class SettingValidatorTestCase(unittest.TestCase):
    
    def test_init_basic(self):
        """ Testing the SettingsValidator class instanciation"""
        valid = SettingValidator('string')
        #trying to call it
        valid('test')

    def test_init_badname(self):
        """ Testing SettingValidator instanciation with non existing validator
            name"""
        with self.assertRaises(LodelFatalError):
            SettingValidator('qklfhsdufgsdyfugigsdfsdlcknsdp')

    def test_noneswitch(self):
        """ Testing the none_is_valid switch given at validator instanciation
        """
        none_invalid = SettingValidator('int')
        none_valid = SettingValidator('int', none_is_valid = True)

        none_valid(None)
        with self.assertRaises(SettingsValidationError):
            none_invalid(None)

    def test_validator_registration(self):
        """ Testing the register_validator method of SettingValidator """
        mockfun = mock.MagicMock()
        vname = 'lfkjdshfkuhsdygsuuyfsduyf'
        testval = 'foo'
        SettingValidator.register_validator(vname, mockfun, 'test validator')
        #Using registered validator
        valid = SettingValidator(vname)
        valid(testval)
        mockfun.assert_called_once_with(testval)

    def test_validator_optargs_forwarding(self):
        """ Testing the ability for SettingValidator to forward optional
            arguments """
        mockfun = mock.MagicMock()
        vname = 'lkjdsfhsdiufhisduguig'
        testval = 'azertyuiop'
        SettingValidator.register_validator(vname, mockfun, 'test validator')
        #Using registered validator with more arguments
        valid = SettingValidator(vname,
            arga = 'a', argb = 42, argc = '1337')
        valid(testval)
        mockfun.assert_called_once_with(
            testval, arga='a', argb=42, argc='1337')
