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


import sys
import os, os.path

sys.path.append(os.path.dirname(os.getcwd()+'/..'))
from lodel.context import LodelContext
LodelContext.init()
from lodel.settings.settings import Settings as settings
settings('globconf.d')
from lodel.settings import Settings

def generate_dyncode(model_file, translator):
    from lodel.editorial_model.model import EditorialModel
    from lodel.leapi import lefactory

    model = EditorialModel.load(translator, filename  = model_file)
    dyncode = lefactory.dyncode_from_em(model)
    return dyncode

def refresh_dyncode(model_file, translator, output_filename):
    dyncode = generate_dyncode(model_file, translator)
    with open(output_filename, 'w+') as out_fd:
        out_fd.write(dyncode)
    out_fd.close()

