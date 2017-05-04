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

from lodel.leapi.datahandlers.base_classes import DataHandler
from lodel.leapi.datahandlers.datas import Varchar


class DataHandlerTestCase(unittest.TestCase):

    def test_init_abstract_class(self):
        datahandler = None
        try:
            datahandler = DataHandler()
        except NotImplementedError:
            self.assertNotIsInstance(datahandler, DataHandler)
            self.assertIsNone(datahandler)

    def test_register_new_handler(self):
        DataHandler.register_new_handler('testvarchar', Varchar)
        self.assertEqual(DataHandler.from_name('testvarchar'), Varchar)

    def test_register_nonclass_as_handler(self):
        try:
            DataHandler.register_new_handler('testvarchar', 'common string')
        except Exception as err:
            self.assertEqual(ValueError, type(err))

    def test_register_invalid_class_as_handler(self):

        try:
            DataHandler.register_new_handler('testvarchar', Exception)
        except Exception as err:
            self.assertEqual(ValueError, type(err))

    def test_from_name(self):
        DataHandler.register_new_handler('test_varchar', Varchar)
        self.assertEqual(DataHandler.from_name('test_varchar'), Varchar)

    def test_from_missing_name(self):
        DataHandler.register_new_handler('test_varchar1', Varchar)
        DataHandler.register_new_handler('test_varchar2', Varchar)
        try:
            DataHandler.from_name('test_varchar3')
        except Exception as err:
            self.assertEqual(NameError, type(err))
