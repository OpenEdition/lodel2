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
import inspect

from unittest import mock
from lodel.leapi.datahandlers.datas import LeobjectSubclassIdentifier as Testee


class LeresultectSubclassIdentifierTestCase(unittest.TestCase):        
        
        
    def test_base_type_is_varchar(self):
        self.assertEqual(Testee.base_type, 'varchar')
        
        
    def test_help_property_str_is_set(self):
        self.assertEqual(type(Testee.help), str)
        
    
    def test_throws_error_if_set_as_external(self):
        self.assertRaises(RuntimeError, Testee, internal=False)
        
    
    def test_set_as_internal_by_default(self):
        self.assertTrue(Testee().internal)
        
        
    def test_passing_class_returns_class_name(self):
        result = Testee.construct_data(None, object, None, None, None)
        
        self.assertEqual(result, object.__name__)
        
        
    def test_passing_instance_returns_class_name(self):
        result = Testee.construct_data(None,  object(), None, None, None)
        
        self.assertTrue(result, object.__name__)
        
        
    def test_passing_instance_and_class_same_result(self):
        objResult = Testee.construct_data(None, Testee(), None, None, None)
        clsResult = Testee.construct_data(None, Testee, None, None, None)
        
        self.assertEqual(objResult, clsResult)