## @package lodel.plugin.datasource_plugin Datasource plugins management module
#
# It contains the base classes for all the datasource plugins that could be added to Lodel


from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin.plugins': ['Plugin'],
    'lodel.plugin.exceptions': ['PluginError', 'PluginTypeError',
        'LodelScriptError', 'DatasourcePluginError'],
    'lodel.validator.validator': ['Validator'],
    'lodel.exceptions': ['LodelException', 'LodelExceptions',
        'LodelFatalError', 'DataNoneValid', 'FieldValidationError']})

## @brief The plugin type that is used in the global settings of Lodel
_glob_typename = 'datasource'


## @brief Main abstract class from which the plugins' datasource classes must inherit.
class AbstractDatasource(object):
    
    ## @brief Trigger LodelFatalError when abtract method called
    # @throw LodelFatalError if there is an attempt to instanciate an object from this class
    @staticmethod
    def _abs_err():
        raise LodelFatalError("This method is abstract and HAVE TO be \
reimplemented by plugin datasource child class")
    
    ##
    # @param *conn_args
    # @param **conn_kwargs
    def __init__(self, *conn_args, **conn_kwargs):
        self._abs_err()

    ## @brief Provides a new uniq numeric ID
    # @param emcomp LeObject subclass (not instance) : defines against which objects type the id should be unique
    # @return int
    def new_numeric_id(self, emcomp):
        self._abs_err()

    ## @brief Returns a selection of documents from the datasource
    # @param target Emclass : class of the documents
    # @param field_list list : fields to get from the datasource
    # @param filters list : List of filters
    # @param rel_filters list : List of relational filters (default value : None)
    # @param order list : List of column to order. ex: order = [('title', 'ASC'),] (default value : None)
    # @param group list : List of tupple representing the column to group together. ex: group = [('title', 'ASC'),] (default value : None)
    # @param limit int : Number of records to be returned (default value None)
    # @param offset int: used with limit to choose the start record (default value : 0)
    # @param instanciate bool : If true, the records are returned as instances, else they are returned as dict (default value : True)
    # @return list
    def select(self, target, field_list, filters, rel_filters=None, order=None, group=None, limit=None, offset=0,
               instanciate=True):
        self._abs_err()

    ## @brief Deletes records according to given filters
    # @param target Emclass : class of the record to delete
    # @param filters list : List of filters
    # @param relational_filters list : List of relational filters
    # @return int : number of deleted records
    def delete(self, target, filters, relational_filters):
        self._abs_err()

    ## @brief updates records according to given filters
    # @param target Emclass : class of the object to insert
    # @param filters list : List of filters
    # @param relational_filters list : List of relational filters
    # @param upd_datas dict : datas to update (new values)
    # @return int : Number of updated records
    def update(self, target, filters, relational_filters, upd_datas):
        self._abs_err()

    ## @brief Inserts a record in a given collection
    # @param target Emclass : class of the object to insert
    # @param new_datas dict : datas to insert
    # @return the inserted uid
    def insert(self, target, new_datas):
        self._abs_err()

    ## @brief Inserts a list of records in a given collection
    # @param target Emclass : class of the objects inserted
    # @param datas_list list : list of dict
    # @return list : list of the inserted records' ids
    def insert_multi(self, target, datas_list):
        self._abs_err()


## @brief Represents a Datasource plugin
#
# It will provide an access to a data collection to LeAPI (i.e. database connector, API ...).
#
# It provides the methods needed to initialize the datasource attribute in LeAPI LeObject child
# classes (see @ref leapi.leobject.LeObject._init_datasources() )
#
# @note For the moment implementation is done with a retro-compatibilities priority and not with a convenience priority.
# @todo Refactor and rewrite lodel2 datasource handling
# @todo Write abstract classes for Datasource and MigrationHandler !!!
class DatasourcePlugin(Plugin):
    
    _type_conf_name = _glob_typename
  
    ## @brief Stores confspecs indicating where DatasourcePlugin list is stored
    _plist_confspecs = {
        'section': 'lodel2',
        'key': 'datasource_connectors',
        'default': 'dummy_datasource',
        'validator': Validator(
            'custom_list', none_is_valid = False,
            validator_name = 'plugin', validator_kwargs = {
                'ptype': _glob_typename,
                'none_is_valid': False})
        }
 
    ##
    # @param name str : plugin's name
    # @see plugins.Plugin
    def __init__(self, name):
        super().__init__(name)
        self.__datasource_cls = None
    
    ## @brief Returns an accessor to the datasource class
    # @return A python datasource class
    # @throw DatasourcePluginError if the plugin's datasource class is not a child of 
    # @ref lodel.plugin.datasource_plugin.AbstractDatasource
    def datasource_cls(self):
        if self.__datasource_cls is None:
            self.__datasource_cls = self.loader_module().Datasource
            if not issubclass(self.__datasource_cls, AbstractDatasource):
                raise DatasourcePluginError("The datasource class of the \
'%s' plugin is not a child class of \
lodel.plugin.datasource_plugin.AbstractDatasource" % (self.name))
        return self.__datasource_cls
    
    ## @brief Returns an accessor to migration handler class
    # @return A python migration handler class
    def migration_handler_cls(self):
        return self.loader_module().migration_handler_class()

    ## @brief Returns an initialized Datasource instance
    # @param ds_name str : The name of the datasource to instanciate
    # @param ro bool : indicates if it will be in read only mode, else it will be in write only mode
    # @return A properly initialized Datasource instance
    @classmethod
    def init_datasource(cls, ds_name, ro):
        plugin_name, ds_identifier = cls.plugin_name(ds_name, ro)
        ds_conf = cls._get_ds_connection_conf(ds_identifier, plugin_name)
        ds_cls = cls.get_datasource(plugin_name)
        return ds_cls(**ds_conf)
    
    ## @brief Returns an initialized MigrationHandler instance
    # @param ds_name str : The datasource name
    # @return A properly initialized MigrationHandler instance
    # @throw PluginError if a read only datasource instance was given to the migration handler. 
    @classmethod
    def init_migration_handler(cls, ds_name):
        plugin_name, ds_identifier = cls.plugin_name(ds_name, False)
        ds_conf = cls._get_ds_connection_conf(ds_identifier, plugin_name)
        mh_cls = cls.get_migration_handler(plugin_name)
        if 'read_only' in ds_conf:
            if ds_conf['read_only']:
                raise PluginError("A read only datasource was given to \
migration handler !!!")
            del(ds_conf['read_only'])
        return mh_cls(**ds_conf)


    ## @brief Given a datasource name returns a DatasourcePlugin name
    # @param ds_name str : datasource name
    # @param ro bool : if true consider the datasource as readonly
    # @return a DatasourcePlugin name
    # @throw DatasourcePluginError if the given datasource is unknown or not configured, or if there is a conflict in its "read-only" property (between the instance and the settings).
    # @throw SettingsError if there are misconfigured datasource settings.
    @staticmethod
    def plugin_name(ds_name, ro):
        LodelContext.expose_modules(globals(), {
            'lodel.settings': ['Settings']})
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

    ## @brief Returns a datasource's configuration
    # @param ds_identifier str : datasource name
    # @param ds_plugin_name : datasource plugin name
    # @return a dict containing datasource initialisation options
    # @throw DatasourcePluginError if a datasource plugin or instance cannot be found
    @staticmethod
    def _get_ds_connection_conf(ds_identifier,ds_plugin_name):
        LodelContext.expose_modules(globals(), {
            'lodel.settings': ['Settings']})
        if ds_plugin_name not in Settings.datasource._fields:
            msg = "Unknown or unconfigured datasource plugin %s"
            msg %= ds_plugin_name
            raise DatasourcePluginError(msg)
        ds_conf = getattr(Settings.datasource, ds_plugin_name)
        if ds_identifier not in ds_conf._fields:
            msg = "Unknown or unconfigured datasource instance %s"
            msg %= ds_identifier
            raise DatasourcePluginError(msg)
        ds_conf = getattr(ds_conf, ds_identifier)
        return {k: getattr(ds_conf,k) for k in ds_conf._fields }

    ## @brief Returns a DatasourcePlugin instance from a plugin's name
    # @param ds_name str : plugin name
    # @return DatasourcePlugin
    # @throw PluginError if no plugin named ds_name found (@see lodel.plugin.plugins.Plugin)
    # @throw PluginTypeError if ds_name ref to a plugin that is not a DatasourcePlugin
    @classmethod
    def get(cls, ds_name):
        pinstance = super().get(ds_name)  # Will raise PluginError if bad name
        if not isinstance(pinstance, DatasourcePlugin):
           raise PluginTypeErrror("A name of a DatasourcePlugin was excepted \
but %s is a %s" % (ds_name, pinstance.__class__.__name__))
        return pinstance

    ## @brief Returns a datasource class given a datasource name
    # @param ds_plugin_name str : datasource plugin name
    # @return Datasource class
    @classmethod
    def get_datasource(cls, ds_plugin_name):
        return cls.get(ds_plugin_name).datasource_cls()
    
    ## @brief Returns a migration handler class, given a plugin name
    # @param ds_plugin_name str : a datasource plugin name
    # @return MigrationHandler class
    @classmethod
    def get_migration_handler(cls, ds_plugin_name):
        return cls.get(ds_plugin_name).migration_handler_cls()


## @page lodel2_datasources Lodel2 datasources
#
# @par lodel2_datasources_intro Introduction
# A single lodel2 website can interact with multiple datasources. This page
# aims to describe configuration and organisation of datasources in lodel2.
# Each object is attached to a datasource. This association is done in the
# editorial model, in which the datasource is identified by its name.
#
# @par Datasources declaration
# To define a datasource you have to write something like this in configuration file :
# <pre>
# [lodel2.datasources.DATASOURCE_NAME]
# identifier = DATASOURCE_FAMILY.SOURCE_NAME
# </pre>
#  See below for DATASOURCE_FAMILY & SOURCE_NAME
#
# @par Datasources plugins
# Each datasource family is a plugin ( @ref plugin_doc "More informations on plugins" ). 
# For example mysql or a mongodb plugins. \n
#
# Here is the CONFSPEC variable templates for datasources plugin
#<pre>
#CONFSPEC = {
#                'lodel2.datasource.example.*' : {
#                    'conf1' : VALIDATOR_OPTS,
#                    'conf2' : VALIDATOR_OPTS,
#                    ...
#                }
#}
#</pre>
# 
#MySQL example \n
#<pre>
#CONFSPEC = {
#                'lodel2.datasource.mysql.*' : {
#                    'host': (   'localhost',
#                                Validator('host')),
#                    'db_name': (    'lodel',
#                                    Validator('string')),
#                    'username': (   None,
#                                    Validator('string')),
#                    'password': (   None,
#                                    Validator('string')),
#                }
#}
#</pre>
#
# @par Configuration example
# <pre>
# [lodel2.datasources.main]
# identifier = mysql.Core
# [lodel2.datasources.revues_write]
# identifier = mysql.Revues
# [lodel2.datasources.revues_read]
# identifier = mysql.Revues
# [lodel2.datasources.annuaire_persons]
# identifier = persons_web_api.example
# ;
# ; Then, in the editorial model you are able to use "main", "revues_write", 
# ; etc as datasource
# ;
# ; Here comes the datasources declarations
# [lodel2.datasource.mysql.Core]
# host = db.core.labocleo.org
# db_name = core
# username = foo
# password = bar
# ;
# [lodel2.datasource.mysql.Revues]
# host = revues.org
# db_name = RO
# username = foo
# password = bar
# ;
# [lodel2.datasource.persons_web_api.example]
# host = foo.bar
# username = cleo
#</pre>
