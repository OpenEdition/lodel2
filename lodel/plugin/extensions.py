from .plugins import Plugin
from .exceptions import *
from lodel.settings.validator import SettingValidator

class Extension(Plugin):
    
    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'extensions',
        'default': [],
        'validator': SettingValidator('list', none_is_valid = False)}

    _type_conf_name = 'extension'

