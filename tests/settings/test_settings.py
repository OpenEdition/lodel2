#
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or  modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import unittest
from unittest import mock

import tests.loader_utils
from lodel.settings.settings import Settings
from lodel.settings.settings import SettingsLoader
from lodel.settings.utils import SettingsError, SettingsErrors

def dummy_validator(value): return value

class SettingsTestCase(unittest.TestCase):
    
    def test_init(self):
        with self.assertRaises(RuntimeError):
            Settings('conf.d')
    
    #@unittest.skip("This tests doesn't pass anymore, but I do not understand why it should pass")
    def test_set(self):

        Settings.set('lodel2.editorialmodel.emfile','test ok', dummy_validator)
        Settings.set('lodel2.editorialmodel.editormode','test ok', dummy_validator)
        loader = SettingsLoader('conf.d')
        option = loader.getoption('lodel2.editorialmodel','emfile', dummy_validator)
        option = loader.getoption('lodel2.editorialmodel','editormode', dummy_validator)
        self.assertEqual(option , 'test ok')
        option = loader.getoption('lodel2.editorialmodel','editormode', dummy_validator)
        self.assertEqual(option, 'test ok')
        Settings.set('lodel2.editorialmodel.emfile','examples/em_test.pickle', dummy_validator)
        Settings.set('lodel2.editorialmodel.editormode','True', dummy_validator)
        
