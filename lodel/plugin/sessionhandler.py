from .plugins import Plugin
from .exceptions import *
from lodel.settings.validator import SettingValidator

##@page lodel2_plugins Lodel2 plugins system
#
# @par Plugin structure
#A plugin is  a package (a folder containing, at least, an __init__.py file.
#This file should expose multiple things :
# - a CONFSPEC variable containing configuration specifications
# - an _activate() method that returns True if the plugin can be activated (
# optionnal)
#
class SessionHandlerPlugin(Plugin):
    __instance = None
    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'session_handler',
        'default': None,
        'validator': SettingValidator('string', none_is_valid=False)}
        
    def __init__(self, plugin_name):
        if self.__instance is None:
            super(Plugin, self).__init__(plugin_name)
            self.__instance = True
        else:
            raise RuntimeError("A SessionHandler Plugin is already plug")

