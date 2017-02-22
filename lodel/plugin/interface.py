from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin.plugins': ['Plugin'],
    'lodel.plugin.exceptions': ['PluginError', 'PluginTypeError',
        'LodelScriptError', 'DatasourcePluginError'],
    'lodel.validator.validator': ['Validator']})

_glob_typename = 'ui'


##@brief Handles interfaces plugin
#@note It's a singleton class. Only 1 interface allowed by instance.
class InterfacePlugin(Plugin):
    
    ##@brief Singleton instance storage
    _instance = None

    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'interface',
        'default': None,
        'validator': Validator(
            'plugin', none_is_valid = True, ptype = _glob_typename)}

    _type_conf_name = _glob_typename
    
    def __init__(self, name):
        if InterfacePlugin._instance is not None:
            raise PluginError("Maximum one interface allowed")
        super().__init__(name)
        self._instance = self

    ##@brief Clear class
    #@see plugins.Plugin::clear()
    @classmethod
    def clear_cls(cls):
        if cls._instance is not None:
            inst = cls._instance
            cls._instance = None
            del(inst)
