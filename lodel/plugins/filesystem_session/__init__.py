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


## @package plugins.filesystem_session This package is a plugin for filesystem based session management

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

__plugin_name__ = 'filesystem_session'
__version__ = [0,0,1]
__plugin_type__ = 'session_handler'
__loader__ = 'main.py'
__confspec__ = "confspec.py"
__author__ = "Lodel2 dev team"
__fullname__ = "FileSystem Session Store Plugin"


## @brief This methods allow plugin writter to write some checks
#
# @return True if checks are OK else returns a string with a reason
def _activate():
    return True
