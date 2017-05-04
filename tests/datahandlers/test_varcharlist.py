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

from lodel.leapi.datahandlers.datas import VarcharList as Testee
from lodel.leapi.datahandlers.exceptions import LodelDataHandlerException
from lodel.exceptions import LodelException

class VarcharListTestCase(unittest.TestCase):
    
    
    string = 'a simple string for testing purpose'
    expected_result = string.split(' ')
    
    
    def test_base_type_is_varchar(self):
        '''base_type property has to be equal to \'varchar\''''
        self.assertEqual(Testee.base_type, 'varchar')
    
    
    def test_help_property_str_is_set(self):
        '''Help property must be set and be a string'''
        self.assertEqual(type(Testee.help), str)
        
        
    def test_default_delimiter_is_set(self):
        '''The DataHandler has to provide a default delimiter if not provided'''
        testee = Testee()

        self.assertTrue(hasattr(testee, 'delimiter'))
    
    
    def test_set_custom_delimiter_success(self):
        '''The custom delimiter isn't set as expected'''
        delimiter = ';'
        testee = Testee(delimiter=delimiter)
        
        self.assertEqual(delimiter, testee.delimiter)
        
    
    def test_custom_delimiter_not_string_raises_error(self):
        '''DataHandler\'s init should raise an exception on trying to pass incorrect type delimiter'''

        self.assertRaises(LodelException, Testee, 123456789)
        
        
    def test_construct_datas_success(self):
        '''Basic usage of VarcharList doesn't behave as expected'''
        string = 'a b c'
        testee = Testee()
        
        actual_result = testee.construct_data(None, None, None, self.string)
        self.assertEqual(self.expected_result, actual_result)
        

    def test_constuct_datas_with_custom_delimiter_success(self):
        '''The use of custom delimiter doesn't work as supposed to !'''
        delimiter = ';'
        string = self.string.replace(' ', delimiter)
        testee = Testee(delimiter=delimiter)
        
        actual_result = testee.construct_data(None, None, None, string)
        self.assertEqual(self.expected_result, actual_result)
