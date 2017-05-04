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

from lodel.leapi.datahandlers.datas import Concat as Testee


class ConcatTestCase(unittest.TestCase):
    
    
    def test_base_type_is_char(self):
        self.assertEqual(Testee.base_type, 'char')
        
        
    def test_help_property_str_is_set(self):
        self.assertEqual(type(Testee.help), str)
        
    
    def test_correctly_sets_format_string(self):
        separator = '-'
        field_list  = ['', '', '']
        testee = Testee(field_list, separator)
        
        self.assertEqual(testee._format_string, separator.join(['%s' for _ in field_list]))
        