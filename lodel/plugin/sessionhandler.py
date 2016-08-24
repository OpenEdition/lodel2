from .plugins import Plugin, MetaPlugType
from .exceptions import *
from lodel.settings.validator import SettingValidator

##@brief SessionHandlerPlugin metaclass designed to implements a wrapper
#between SessionHandlerPlugin classmethod and plugin loader functions
class SessionPluginWrapper(MetaPlugType):
    ##@brief Constant that stores all possible session actions
    #
    #Key is the SessionHandlerPlugin method name and value is SessionHandler
    #plugin function name
    _ACTIONS = {
        'start': 'start_session',
        'destroy': 'destroy_session', 
        'restore': 'restore_session',
        'save': 'save_session'}

    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)
        
    ##@brief Handles wrapper between class method and plugin loader functions
    def __get_attribute__(self, name):
        if name in SessionPluginWrapper._Actions:
            return getattr(
                self._instance.loader_module(),
                SessionPluginWrapper._Actions[name])
        return super().__get_attribute__(name)


##@page lodel2_plugins Lodel2 plugins system
#
# @par Plugin structure
#A plugin is  a package (a folder containing, at least, an __init__.py file.
#This file should expose multiple things :
# - a CONFSPEC variable containing configuration specifications
# - an _activate() method that returns True if the plugin can be activated (
# optionnal)
#
class SessionHandlerPlugin(Plugin, metaclass=SessionPluginWrapper): 
    ##@brief Stores the singleton instance
    _instance = None

    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'session_handler',
        'default': None,
        'validator': SettingValidator('string', none_is_valid=False)}
            
    def __init__(self, plugin_name):
        if self._instance is None:
            super(Plugin, self).__init__(plugin_name)
            self._instance = self
        else:
            raise RuntimeError("A SessionHandler Plugin is already plug")
