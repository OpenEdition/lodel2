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


## @package lodel.plugin.extensions A package to manage the Extension plugins


from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin.plugins': ['Plugin'],
    'lodel.plugin.exceptions': ['PluginError', 'PluginTypeError',
        'LodelScriptError', 'DatasourcePluginError'],
    'lodel.validator.validator': ['Validator']})

_glob_typename = 'extension'

## @brief A class representing a basic Extension plugin
# 
# This class will be extended for each plugin of this type.
class Extension(Plugin):
    
    ## @brief Specifies the settings linked to this plugin
    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'extensions',
        'default': None,
        'validator': Validator(
            'custom_list', none_is_valid = True,
            validator_name = 'plugin', validator_kwargs = {
                'ptype': _glob_typename,
                'none_is_valid': False})
        }
    
    ## @brief A property defining the type's name of this plugin.
    # By default, it's the global type name ("extension" here).
    _type_conf_name = _glob_typename

