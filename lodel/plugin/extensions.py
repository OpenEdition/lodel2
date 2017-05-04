## @package lodel.plugin.extensions A package to manage the Extension plugins


from lodel.plugin.plugins import Plugin
from lodel.plugin.exceptions import PluginError, PluginTypeError, LodelScriptError, DatasourcePluginError
from lodel.validator.validator import Validator

_glob_typename = 'extension'

## @brief A class representing a basic Extension plugin
# 
# This class will be extended for each plugin of this type.
class Extension(Plugin):
    
    ## @brief Specifies the settings linked to this plugin
    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'extensions',
        'default': None,
        'validator': Validator(
            'custom_list', none_is_valid = True,
            validator_name = 'plugin', validator_kwargs = {
                'ptype': _glob_typename,
                'none_is_valid': False})
        }
    
    ## @brief A property defining the type's name of this plugin.
    # By default, it's the global type name ("extension" here).
    _type_conf_name = _glob_typename

