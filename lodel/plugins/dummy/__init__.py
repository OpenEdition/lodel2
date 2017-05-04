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


## @package lodel.plugins.dummy Basic plugin used as a template for developping new plugins

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

## @brief plugin's name (matching the package's name)
__plugin_name__ = "dummy"
## @brief plugin's version
__version__ = '0.0.1' #or __version__ = [0,0,1]
## @brief plugin's loader module
__loader__ = "main.py"
## @brief plugin's options' definition module
__confspec__ = "confspec.py"
## @brief plugin's author(s)
__author__ = "Lodel2 dev team"
## @brief plugin's full name
__fullname__ = "Dummy plugin"
__name__ = 'dummy'
## @brief plugin's category
__plugin_type__ = 'extension'


## @brief This methods allow plugin writter to write some checks
#
# @return bool : True if checks are OK else return a string with a reason
def _activate():
    import leapi_dyncode
    print("Testing dynamic objects : ")
    print("Object : ", leapi_dyncode.Object)
    print("Publication : ", leapi_dyncode.Publication)
    print("Publication fields : ", leapi_dyncode.Publication.fieldnames())
    return True
