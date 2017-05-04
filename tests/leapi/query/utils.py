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


#
# Importing this file trigger dynamic code generation & load
#
# To use dynamic code import utils.dyncode_module as dyncode

import tempfile
import os
from importlib.machinery import SourceFileLoader

from lodel.leapi.lefactory import dyncode_from_em
from lodel.editorial_model.translator import picklefile

from tests import loader_utils

def init_dyncode():
    f_handler, dyncode_file = tempfile.mkstemp( prefix="lodel2_tests",
                                            suffix="_dyncode")
    os.close(f_handler)
    model = picklefile.load('tests/editorial_model.pickle')
    source_code = dyncode_from_em(model)
    with os.fdopen(os.open(dyncode_file, os.O_WRONLY), 'w') as dynfd:
        dynfd.write(source_code)
    dyncode_module = SourceFileLoader("lodel.dyncode", dyncode_file).load_module()
    os.unlink(dyncode_file)
    return dyncode_module

dyncode_module = init_dyncode()

