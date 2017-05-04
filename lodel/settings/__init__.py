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


## @package lodel.settings Lodel2 settings package
#
# @par Configuration files
# The configurations files are in ini format (thank's python ConfigParser...).
# To know how the settings are validated and specified see
# @ref lodel.settings.validator and @ref howto_writeplugin_basicstruct
# The configuration is divided in two parts :
#- a global configuration file that contains
# - the path to the lodel2 lib directory
# - the paths of directories containing plugins
#- a conf.d directories containing multiple configuration files
#  
# @par Bootstrap/load/use in lodel instance
# To use Settings in production you have to write a loader that will bootstrap
# the Settings class allowing @ref lodel.settings.__init__.py to expose a copy
# of the lodel.settings.Settings representation of the
# @ref lodel.settings.settings.Settings.__confs . Here is an example of 
# loader file :
# <pre>
# #-*- coding: utf-8 -*-
# from lodel.settings.settings import Settings
# Settings.bootstrap(
#                       conf_file = 'somepath/settings_local.ini',
#                       conf_dir = 'somepath/conf.d')
# </pre>
# Once this file is imported it allows to all lodel2 modules to use settings
# like this :
# <pre>
# from lodel.settings import Settings
# if Settings.debug:
#   print("DEBUG MODE !")
# </pre>
#
from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.settings': [('SettingsRO', 'Settings')]})

