class PluginError(Exception):
    pass

class PluginTypeError(PluginError):
    pass

class LodelScriptError(Exception):
    pass

class DatasourcePluginError(PluginError):
    pass
