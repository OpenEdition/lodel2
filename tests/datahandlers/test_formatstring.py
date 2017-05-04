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

from lodel.leapi.datahandlers.datas import FormatString
from lodel.editorial_model.components import EmClass

class FormatStringTestCase(unittest.TestCase):

        
    def test_base_type_is_char(self):
        self.assertEqual(FormatString.base_type, 'char')
        
        
    def test_help_property_str_is_set(self):
        self.assertEqual(type(FormatString.help), str)


    def test_string_formatting_output(self):
        testee = FormatString(self.regex,[self.fone_name, self.ftwo_name])
        
        expected_result = self.regex % (self.field_one_value, self.field_two_value)
        actual_result = testee.construct_data(self.dummyEmClass, None, self.field_value_dict, None)

        self.assertEqual(actual_result, expected_result)
        
        
    def test_throws_user_warning_on_exceeding_string(self):
        max_length = len(self.regex % (self.field_one_value, self.field_two_value)) / 2
        testee = FormatString(self.regex, self.field_list, max_length=self.max_length)
        
        self.assertWarns(
            UserWarning,
            testee.construct_data,
            self.dummyEmClass, None, self.field_value_dict, None
        )
            
            
    def test_exceeding_string_length_is_truncated(self):
        max_length = 2
        testee = FormatString(self.regex, self.field_list, max_length=self.max_length)
        result_string = testee._construct_data(self.dummyEmClass, None, self.field_value_dict, None)
        
        self.assertEqual(self.max_length, len(result_string))
        
            
    def test_thrown_exceeding_str_warning_message_composition(self):
        testee = FormatString(self.regex, self.field_list, max_length=self.max_length)
        
        self.assertWarnsRegex(
            UserWarning,
            '[T|t]runcat[a-z]+',
            testee.construct_data,
            self.dummyEmClass, None, self.field_value_dict, None
        )
            
    
    def setUp(self):
        self.regex = '%s-%s'
        self.dummyEmClass = EmClass('testing')
        self.fone_name = 'field1'
        self.ftwo_name = 'field2'
        self.dummyEmClass.new_field(self.fone_name, 'varchar')
        self.dummyEmClass.new_field(self.ftwo_name, 'varchar')
        self.field_one_value = 'field one value'
        self.field_two_value = 'field two value'
        self.field_value_dict = {self.fone_name: self.field_one_value, self.ftwo_name: self.field_two_value}
        self.field_list = [self.fone_name, self.ftwo_name]
        
        self.max_length = round(len(self.regex % (self.field_one_value, self.field_two_value)) / 2)
        