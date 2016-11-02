from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin.plugins': ['Plugin'],
    'lodel.plugin.exceptions': ['PluginError', 'PluginTypeError',
        'LodelScriptError', 'DatasourcePluginError'],
    'lodel.settings.validator': ['SettingValidator']})

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

