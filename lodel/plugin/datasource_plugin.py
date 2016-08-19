from .plugins import Plugin
from .exceptions import *
from lodel.settings.validator import SettingValidator

##@brief Designed to handles datasources plugins
#
#A datasource provide data access to LeAPI typically a connector on a DB
#or an API
#@note For the moment implementation is done with a retro-compatibilities
#priority and not with a convenience priority.
#@todo Refactor and rewrite lodel2 datasource handling
class DatasourcePlugin(Plugin):
    
    ##@brief Stores confspecs indicating where DatasourcePlugin list is stored
    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'datasource_connectors',
        'default': None,
        'validator': SettingValidator('strip', none_is_valid = False) }
    
    def __init__(self, name):
        super().__init__(name)
        self.__datasource_cls = None

    def datasource_cls(self):
        if self.__datasource_cls is None:
            self.__datasource_cls = self.loader_module().Datasource
        return self.__datasource_cls

    def migration_handler(self):
        return self.loader_module().migration_handler_class()

    ##@brief Return an initialized Datasource instance
    #@param ds_name str : The name of the datasource to instanciate
    #@param ro bool
    #@return A properly initialized Datasource instance
    #@throw SettingsError if an error occurs in settings
    #@throw DatasourcePluginError for various errors
    @classmethod
    def init_datasource(cls, ds_name, ro):
        plugin_name, ds_identifier = cls.plugin_name(ds_name, ro)
        ds_conf = cls._get_ds_connection_conf(ds_identifier, plugin_name)
        ds_cls = cls.get_datasource(plugin_name)
        return ds_cls(**ds_conf)

    ##@brief Given a datasource name returns a DatasourcePlugin name
    #@param ds_name str : datasource name
    #@param ro bool : if true consider the datasource as readonly
    #@return a DatasourcePlugin name
    #@throw PluginError if datasource name not found
    #@throw DatasourcePermError if datasource is read_only but ro flag arg is
    #false
    @staticmethod
    def plugin_name(ds_name, ro):
        from lodel.settings import Settings
        # fetching connection identifier given datasource name
        try:
            ds_identifier = getattr(Settings.datasources, ds_name)
        except (NameError, AttributeError):
            raise DatasourcePluginError("Unknown or unconfigured datasource \
'%s'" % ds_name)
        # fetching read_only flag
        try:
            read_only = getattr(ds_identifier, 'read_only')
        except (NameError, AttributeError):
            raise SettingsError("Malformed datasource configuration for '%s' \
: missing read_only key" % ds_name)
        # fetching datasource identifier
        try:
            ds_identifier = getattr(ds_identifier, 'identifier')
        except (NameError,AttributeError) as e:
            raise SettingsError("Malformed datasource configuration for '%s' \
: missing identifier key" % ds_name)
        # settings and ro arg consistency check
        if read_only and not ro:
            raise DatasourcePluginError("ro argument was set to False but \
True found in settings for datasource '%s'" % ds_name)
        res = ds_identifier.split('.')
        if len(res) != 2:
            raise SettingsError("expected value for identifier is like \
DS_PLUGIN_NAME.DS_INSTANCE_NAME. But got %s" % ds_identifier)
        return res

    ##@brief Try to fetch a datasource configuration
    #@param ds_identifier str : datasource name
    #@param ds_plugin_name : datasource plugin name
    #@return a dict containing datasource initialisation options
    #@throw NameError if a datasource plugin or instance cannot be found
    @staticmethod
    def _get_ds_connection_conf(ds_identifier,ds_plugin_name):
        from lodel.settings import Settings
        if ds_plugin_name not in Settings.datasource._fields:
            msg = "Unknown or unconfigured datasource plugin %s"
            msg %= ds_plugin
            raise DatasourcePluginError(msg)
        ds_conf = getattr(Settings.datasource, ds_plugin_name)
        if ds_identifier not in ds_conf._fields:
            msg = "Unknown or unconfigured datasource instance %s"
            msg %= ds_identifier
            raise DatasourcePluginError(msg)
        ds_conf = getattr(ds_conf, ds_identifier)
        return {k: getattr(ds_conf,k) for k in ds_conf._fields }

    ##@brief DatasourcePlugin instance accessor
    #@param ds_name str : plugin name
    #@return a DatasourcePlugin instance
    #@throw PluginError if no plugin named ds_name found
    #@throw PluginTypeError if ds_name ref to a plugin that is not a 
    #DatasourcePlugin
    @classmethod
    def get(cls, ds_name):
        pinstance = super().get(ds_name) #Will raise PluginError if bad name
        if not isinstance(pinstance, DatasourcePlugin):
           raise PluginTypeErrror("A name of a DatasourcePlugin was excepted \
but %s is a %s" % (ds_name, pinstance.__class__.__name__))
        return pinstance

    ##@brief Return a datasource class given a datasource name
    #@param ds_name str : datasource plugin name
    #@throw PluginError if ds_name is not an existing plugin name
    #@throw PluginTypeError if ds_name is not the name of a DatasourcePlugin
    @classmethod
    def get_datasource(cls, ds_plugin_name):
        return cls.get(ds_plugin_name).datasource_cls()

    @classmethod
    def get_migration_handler(cls, ds_plugin_name):
        return cls.get(ds_plugin_name).migration_handler_class()
 
