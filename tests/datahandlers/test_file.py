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


import os
import unittest
import tempfile

from lodel.leapi.datahandlers.datas import File, Varchar


class FileTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_file, cls.test_file_path = tempfile.mkstemp()

    def test_check_correct_data_value(self):

        test_file = File()

        test_value = os.path.abspath(os.path.join(os.path.curdir,'test_file.txt'))
        _, error = test_file.check_data_value(test_value)
        self.assertIsNone(error)

    @unittest.skip
    def test_check_uncorrect_data_value(self):
        test_file = File()
        test_bad_value = "invalid_path"
        _, error = test_file.check_data_value(test_bad_value)
        self.assertIsNotNone(test_bad_value)

    def test_can_override(self):
        test_file = File()

        test_file2 = File()
        self.assertTrue(test_file.can_override(test_file2))

        test_varchar = Varchar()
        self.assertFalse(test_file.can_override(test_varchar))

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.test_file_path)