from .plugins import Plugin
from .exceptions import *
from lodel.settings.validator import SettingValidator

class InterfacePlugin(Plugin):
    
    ##@brief Singleton instance storage
    _instance = None

    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'interface',
        'default': None,
        'validator': SettingValidator('strip', none_is_valid = True)}
    
    def __init__(self, name):
        if InterfacePlugin._instance is not None:
            raise PluginError("Maximum one interface allowed")
        super().__init__(name)
        self._instance = self
