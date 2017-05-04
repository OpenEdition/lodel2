#
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or  modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import unittest
from unittest import mock
from unittest.mock import patch

from lodel.exceptions import *
from lodel.validator.validator import *

class ValidatorTestCase(unittest.TestCase):
    
    def test_init_basic(self):
        """ Testing the SettingsValidator class instanciation"""
        valid = Validator('string')
        #trying to call it
        valid('test')

    def test_init_badname(self):
        """ Testing Validator instanciation with non existing validator
            name"""
        with self.assertRaises(LodelFatalError):
            Validator('qklfhsdufgsdyfugigsdfsdlcknsdp')

    def test_noneswitch(self):
        """ Testing the none_is_valid switch given at validator instanciation
        """
        none_invalid = Validator('int')
        none_valid = Validator('int', none_is_valid = True)

        none_valid(None)
        with self.assertRaises(ValidationError):
            none_invalid(None)

    def test_validator_registration(self):
        """ Testing the register_validator method of Validator """
        mockfun = mock.MagicMock()
        vname = 'lfkjdshfkuhsdygsuuyfsduyf'
        testval = 'foo'
        Validator.register_validator(vname, mockfun, 'test validator')
        #Using registered validator
        valid = Validator(vname)
        valid(testval)
        mockfun.assert_called_once_with(testval)

    def test_validator_optargs_forwarding(self):
        """ Testing the ability for Validator to forward optional
            arguments """
        mockfun = mock.MagicMock()
        vname = 'lkjdsfhsdiufhisduguig'
        testval = 'azertyuiop'
        Validator.register_validator(vname, mockfun, 'test validator')
        #Using registered validator with more arguments
        valid = Validator(vname,
            arga = 'a', argb = 42, argc = '1337')
        valid(testval)
        mockfun.assert_called_once_with(
            testval, arga='a', argb=42, argc='1337')
