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


## @package lodel.plugin.interface Handles the Interface type plugins

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin.plugins': ['Plugin'],
    'lodel.plugin.exceptions': ['PluginError', 'PluginTypeError',
        'LodelScriptError', 'DatasourcePluginError'],
    'lodel.validator.validator': ['Validator']})

## @brief Global type name used in the settings of Lodel for this type of plugins
_glob_typename = 'ui'


##@brief A plugin Interface
#@note It's a singleton class. Only 1 interface allowed by instance.
class InterfacePlugin(Plugin):
    
    ## @brief Singleton instance storage
    _instance = None

    ## @brief Settings description
    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'interface',
        'default': None,
        'validator': Validator(
            'plugin', none_is_valid = True, ptype = _glob_typename)}

    ## @brief plugin type name
    _type_conf_name = _glob_typename
    
    ##
    # @param name str : Name of the interface plugin
    # @throw PluginError if there is already an interface plugin instanciated
    def __init__(self, name):
        if InterfacePlugin._instance is not None:
            raise PluginError("Maximum one interface allowed")
        super().__init__(name)
        self._instance = self

    ## @brief Clears the singleton from its active instance
    # @see plugins.Plugin::clear()
    @classmethod
    def clear_cls(cls):
        if cls._instance is not None:
            inst = cls._instance
            cls._instance = None
            del(inst)
