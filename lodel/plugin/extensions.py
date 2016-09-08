from .plugins import Plugin
from .exceptions import *
from lodel.settings.validator import SettingValidator

_glob_typename = 'extension'
class Extension(Plugin):
    
    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'extensions',
        'default': None,
        'validator': SettingValidator(
            'custom_list', none_is_valid = True,
            validator_name = 'plugin', validator_kwargs = {
                'ptype': _glob_typename,
                'none_is_valid': False})
        }

    _type_conf_name = _glob_typename

