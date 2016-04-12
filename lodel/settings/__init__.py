#-*- coding: utf-8 -*-

## @package lodel.settings Lodel2 settings package
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

from lodel.settings.settings import Settings as SettingsHandler

##@brief Bootstraped instance
settings = SettingsHandler.bootstrap()
if settings is not None:
    ##@brief Exposed variable that represents configurations values in a
    # namedtuple tree
    Settings = settings.confs
