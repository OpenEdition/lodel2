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


##@package lodel.editorial_model.translator.picklefile
# This module handles the file storage of an editorial model

import pickle
from pickle import Pickler

##@brief Saves a model in a file
# @param model EditorialModel : the model to save
# @param filename str|None : if None return the model as pickle bytes (by default : None)
# @return None if filename is a string, else returns bytes representation of model
def save(model, filename = None):
    with open(filename, 'w+b') as ffd:
        pickle.dump(model, ffd)
    return filename

##@brief Loads a model from a file
# @param filename str : the filename to use to load the model
# @return EditorialModel
def load(filename):
    with open(filename, 'rb') as ffd:
        edmod = pickle.load(ffd)
    return edmod
