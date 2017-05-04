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
from lodel.leapi.datahandlers.datas import Varchar, Integer
from lodel.leapi.datahandlers.base_classes import FieldValidationError
from lodel.exceptions import *

test_varchar = Varchar(max_length=10)
class VarcharTestCase(unittest.TestCase):

    def test_check_good_data_value(self):
        for test_value in ["c" * 10, "c" * 9]:
            value = test_varchar._check_data_value(test_value)
            self.assertEqual(value, test_value)

    def test_check_bad_data_value(self):
        for test_value in ["c" * 11]:
            with self.assertRaises(FieldValidationError):
                value = test_varchar._check_data_value(test_value)

    def test_can_override(self):
        test_varchar1 = Varchar()
        test_integer = Integer()
        test_varchar2 = Varchar()

        self.assertFalse(test_varchar1.can_override(test_integer))
        self.assertTrue(test_varchar1.can_override(test_varchar2))
