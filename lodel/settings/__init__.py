#-*- coding: utf-8 -*-

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
from lodel.settings.settings import SettingsRO as Settings

