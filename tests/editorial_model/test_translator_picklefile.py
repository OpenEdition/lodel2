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
import tempfile
import os

import tests.loader_utils
from lodel.editorial_model.translator import picklefile
from lodel.editorial_model.model import EditorialModel
from lodel.editorial_model.components import *
from lodel.editorial_model.exceptions import *

class PickleFileTestCase(unittest.TestCase):
    
    def test_save(self):
        model = EditorialModel("test model", description = "Test EM")
        cls1 = model.new_class('testclass1', display_name = 'Classe de test 1', help_text = 'super aide')
        c1f1 = cls1.new_field('testfield1', data_handler = 'varchar')
        c1f2 = cls1.new_field('testfield2', data_handler = 'varchar')
        cls2 = model.new_class('testclass2')
        c2f1 = cls2.new_field('testfield1', data_handler = 'varchar')
        c2f2 = cls2.new_field('testfield2', data_handler = 'varchar')

        grp1 = model.new_group('testgroup1')
        grp1.add_components((cls1, c1f1))
        grp2 = model.new_group('testgroup2')
        grp2.add_components((cls2, c1f2, c2f1, c2f2))

        grp2.add_dependency(grp1)
        
        tmpfd, temp_file = tempfile.mkstemp()
        os.close(tmpfd)
        os.unlink(temp_file)

        model.save(picklefile, filename=temp_file)
        new_model = model.load(picklefile, filename=temp_file)

        self.assertNotEqual(id(new_model), id(model))
        self.assertEqual(new_model.d_hash(), model.d_hash())

        os.unlink(temp_file)



