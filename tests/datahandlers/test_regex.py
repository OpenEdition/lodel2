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
from lodel.exceptions import *
from lodel.leapi.datahandlers.datas import Regex, Varchar, Integer, UniqID
from lodel.leapi.datahandlers.base_classes import DataHandler
from unittest.mock import Mock
import re

class RegexTestCase(unittest.TestCase):
                
                
    def test_invalid_regex_throws_TypeError(self):
        self.assertRaises(TypeError, Regex().__init__, object)
                
                
    def test_compiled_re_property_is_set(self):
        self.assertIs(self.testee.compiled_re, re.compile(self.testee.regex))
    
    
    def test_exceeding_value_length_throws_FieldValidationError(self):
        self.assertRaises(
            FieldValidationError,
            self.testee._check_data_value,
            self.valid_value*self.max_length
        )
        
            
    def test_invalid_field_value_throws_FieldValidationError(self):
        self.assertRaises(
            FieldValidationError,
            self.testee._check_data_value,
            ''
        )
        
            
    def test_valid_field_value_is_returned(self):
        self.assertEqual(self.valid_value, self.testee._check_data_value(self.valid_value))
        
        
    def test_can_override_returns_false_if_different_datahandler_base_type(self):
        mock = self._get_datahandler_mock()
        mock.__class__.base_type = self.testee.base_type*2
 
        self.assertFalse(self.testee.can_override(mock))
        
        
    def test_can_override_returns_false_if_different_datahandler_maxlen(self):
        mock = self._get_datahandler_mock()
        mock.__class__.max_length = self.max_length*2

        self.assertFalse(self.testee.can_override(mock))

        
    def test_can_override_returns_true_if_overridable(self):
        self.assertTrue(self.testee.can_override(self._get_datahandler_mock()))
        
    
    def _get_datahandler_mock(self):
        dataHandlerMock = Mock()
        dataHandlerMock.__class__.base_type = self.testee.base_type
        dataHandlerMock.__class__.max_length = self.testee.max_length
        
        return dataHandlerMock
    
    
    def setUp(self):
        self.max_length = 15
        self.regex = '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        self.valid_value = '126.205.255.12'
        self.testee = Regex(self.regex, self.max_length)
        