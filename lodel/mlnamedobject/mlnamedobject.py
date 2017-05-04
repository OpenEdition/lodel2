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


from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.utils.mlstring': ['MlString']})

## @package lodel.mlnamedobject.mlnamedobject Lodel2 description of objects module
#
# Display name and Description of a lodel2 object

## @brief Represents a multi-language object (dealing with its translations) 
class MlNamedObject(object):
    
    ##
    # @param display_name str|dict : displayed string to name the object (either a string or a dictionnary of the translated strings can be passed)
    # @param help_text str|dict : description text for this object (either a string or a dictionnary of the translated strings can be passed)
    def __init__(self, display_name=None, help_text=None):
        ## @brief The object's name which will be used in all the user interfaces
        self.display_name = None if display_name is None else MlString(display_name)
        ## @brief Description text for this object
        self.help_text = None if help_text is None else MlString(help_text)
