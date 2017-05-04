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


## @package lodel.editorial_model.exceptions
# This module contains the specific exceptions related to the EditorialModel Management.


## @brief Raises an Editorial Model specific exception.
class EditorialModelError(Exception):
    pass


## @brief Tries to import the settings module.
# @raise EditorialModelError
def assert_edit():
    try:
        from lodel import Settings
    except ImportError:  # Very dirty, but don't know how to fix the tests
        return
    if not Settings.editorialmodel.editormode:
        raise EditorialModelError("EM is readonly : editormode is OFF")

