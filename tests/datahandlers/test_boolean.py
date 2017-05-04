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

from lodel.leapi.datahandlers.datas import Boolean, Varchar, Integer


test_boolean = Boolean()
class BooleanTestCase(unittest.TestCase): 

    def test_boolean_good_check_data_value(self):
        for test_value in [True, False]:
            value = test_boolean._check_data_value(test_value)
            self.assertEqual(value, bool(test_value))

    def test_boolean_bad_check_data_value(self):
        for test_value in ['ok', 'True', 'False']:
            with self.assertRaises(FieldValidationError):
                test_boolean._check_data_value(test_value)

    def test_can_override(self):

        test_varchar = Varchar()
        test_int = Integer()

        self.assertFalse(test_boolean.can_override(test_varchar))
        self.assertFalse(test_boolean.can_override(test_int))
