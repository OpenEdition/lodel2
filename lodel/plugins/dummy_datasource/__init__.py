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


## @package lodel.plugins.dummy_datasource Example of a datasource type plugin

# Here we use the Lodel Context Manager to expose the modules which are specific to the application
from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})
from .datasource import DummyDatasource as Datasource

## @brief plugin's category
__plugin_type__ = 'datasource'
## @brief plugin's name (matching the package's name)
__plugin_name__ = "dummy_datasource"
## @brief plugin's version
__version__ = '0.0.1'
## @brief plugin's main entry module
__loader__ = 'main.py'
## @brief plugin's dependances
__plugin_deps__ = []

## @brief Plugin's configuration options and their corresponding validators
CONFSPEC = {
    'lodel2.datasource.dummy_datasource.*' : {
        'dummy': (  None,
                    Validator('dummy', none_is_valid=True))}
}


