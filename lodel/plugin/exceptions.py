class PluginError(Exception):
    pass

class PluginVersionError(PluginError):
    pass

class PluginTypeError(PluginError):
    pass

class LodelScriptError(Exception):
    pass

class DatasourcePluginError(PluginError):
    pass
