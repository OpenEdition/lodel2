from .plugins import Plugin
from .exceptions import *
from lodel.settings.validator import SettingValidator

_glob_typename = 'extension'
class Extension(Plugin):
    
    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'extensions',
        'default': [],
        'validator': SettingValidator(
            'plugin', none_is_valid = False, ptype = _glob_typename)}

    _type_conf_name = _glob_typename

