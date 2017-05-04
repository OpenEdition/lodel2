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
import datetime
from lodel.leapi.datahandlers.datas import DateTime
from lodel.exceptions import *


class DatetimeTestCase(unittest.TestCase):

    def test_datetime_check_data_value(self):
        test_datetime = DateTime()
        for test_value in ['2016-01-01']:
            value = test_datetime._check_data_value(test_value)
            self.assertEqual(value, datetime.datetime(2016, 1, 1, 0, 0))

    def test_datetime_check_data_value_with_custom_format(self):
        test_value = '2016-01-01T10:20:30Z'
        test_datetime = DateTime(format='%Y-%m-%dT%H:%M:%SZ')
        value = test_datetime._check_data_value(test_value)
        self.assertEqual(value, datetime.datetime(2016, 1, 1, 10, 20, 30))

    def test_check_bad_value(self):
        test_datetime = DateTime(now_on_create=True, now_on_update=True)
        for test_value in ['2016-01-01-test', '2016/01/01', 2016]:
            with self.assertRaises(FieldValidationError):
                test_datetime._check_data_value(test_value)
