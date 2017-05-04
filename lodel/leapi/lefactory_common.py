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


#-
#-  THE CONTENT OF THIS FILE IS DESIGNED TO BE INCLUDED IN DYNAMICALLY
#-  GENERATED CODE
#-
#- All lines that begins with #- will be deleted from dynamically generated
#- code...

##@brief Returns a dynamically generated class given its name
#@param name str : The dynamic class name
#@return False or a child class of LeObject
def name2class(name):
    if name not in dynclasses_dict:
        return False
    return dynclasses_dict[name]


##@brief Returns a dynamically generated class given its name
#@note Case insensitive version of name2class
#@param name str
#@return False or a child class of LeObject
def lowername2class(name):
    name = name.lower()
    new_dict = {k.lower():v for k,v in dynclasses_dict.items()}
    if name not in new_dict:
        return False
    return new_dict[name]


##@brief Triggers dynclasses datasources initialisation
@LodelHook("lodel2_plugins_loaded")
def lodel2_dyncode_datasources_init(self, caller, payload):
    for cls in dynclasses:
        cls._init_datasources()
    LodelContext.expose_modules(globals(), {'lodel.plugin.hooks': ['LodelHook']})
    LodelHook.call_hook("lodel2_dyncode_loaded", __name__, dynclasses)
