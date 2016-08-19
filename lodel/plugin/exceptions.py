class PluginError(Exception):
    pass

class PluginTypeErrror(PluginError):
    pass

class LodelScriptError(Exception):
    pass

class DatasourcePluginError(PluginError):
    pass
