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


## @package lodel.plugins.filesystem_session.filesystem_session Session objects management module

## @brief An extended dictionary representing a session in the file system
class FileSystemSession(dict):

    ##
    # @param token str
    def __init__(self, token):
        self.__token = token
        self.__path = None

    ## @brief token getter
    # @return str
    @property
    def token(self):
        return self.__token

    ## @brief path getter
    # @return str
    @property
    def path(self):
        return self.__path

    ## @brief path setter
    # @param path str
    @path.setter
    def path(self, path):
        self.__path = path
