from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin.plugins': ['Plugin'],
    'lodel.plugin.exceptions': ['PluginError', 'PluginTypeError',
        'LodelScriptError', 'DatasourcePluginError'],
    'lodel.validator.validator': ['Validator'],
    'lodel.exceptions': ['LodelException', 'LodelExceptions',
        'LodelFatalError', 'DataNoneValid', 'FieldValidationError']})

_glob_typename = 'datasource'


##@brief Datasource class in plugins HAVE TO inherit from this abstract class
class AbstractDatasource(object):
    
    ##@brief Trigger LodelFatalError when abtract method called
    @staticmethod
    def _abs_err():
        raise LodelFatalError("This method is abstract and HAVE TO be \
reimplemented by plugin datasource child class")
    
    ##@brief The constructor
    def __init__(self, *conn_args, **conn_kwargs):
        self._abs_err()

    ##@brief Provide a new uniq numeric ID
    #@param emcomp LeObject subclass (not instance) : To know on wich things we
    #have to be uniq
    #@return an integer
    def new_numeric_id(self, emcomp):
        self._abs_err()

    ##@brief returns a selection of documents from the datasource
    #@param target Emclass
    #@param field_list list
    #@param filters list : List of filters
    #@param rel_filters list : List of relational filters
    #@param order list : List of column to order. ex: order = [('title', 'ASC'),]
    #@param group list : List of tupple representing the column to group together. ex: group = [('title', 'ASC'),]
    #@param limit int : Number of records to be returned
    #@param offset int: used with limit to choose the start record
    #@param instanciate bool : If true, the records are returned as instances, else they are returned as dict
    #@return list
    def select(self, target, field_list, filters, relational_filters=None,
            order=None, group=None, limit=None, offset=0, instanciate=True):
        self._abs_err()

    ##@brief Deletes records according to given filters
    #@param target Emclass : class of the record to delete
    #@param filters list : List of filters
    #@param relational_filters list : List of relational filters
    #@return int : number of deleted records
    def delete(self, target, filters, relational_filters):
        self._abs_err()

    ## @brief updates records according to given filters
    #@param target Emclass : class of the object to insert
    #@param filters list : List of filters
    #@param relational_filters list : List of relational filters
    #@param upd_datas dict : datas to update (new values)
    #@return int : Number of updated records
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


##@brief Designed to handles datasources plugins
#
#A datasource provide data access to LeAPI typically a connector on a DB
#or an API
#
#Provide methods to initialize datasource attribute in LeAPI LeObject child
#classes (see @ref leapi.leobject.LeObject._init_datasources() )
#
#@note For the moment implementation is done with a retro-compatibilities
#priority and not with a convenience priority.
#@todo Refactor and rewrite lodel2 datasource handling
#@todo Write abstract classes for Datasource and MigrationHandler !!!
class DatasourcePlugin(Plugin):
    
    _type_conf_name = _glob_typename
    ##@brief Stores confspecs indicating where DatasourcePlugin list is stored
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
 
    ##@brief Construct a DatasourcePlugin 
    #@param name str : plugin name
    #@see plugins.Plugin
    def __init__(self, name):
        super().__init__(name)
        self.__datasource_cls = None
    
    ##@brief Accessor to the datasource class
    #@return A python datasource class
    def datasource_cls(self):
        if self.__datasource_cls is None:
            self.__datasource_cls = self.loader_module().Datasource
            if not issubclass(self.__datasource_cls, AbstractDatasource):
                raise DatasourcePluginError("The datasource class of the \
'%s' plugin is not a child class of \
lodel.plugin.datasource_plugin.AbstractDatasource" % (self.name))
        return self.__datasource_cls
    
    ##@brief Accessor to migration handler class
    #@return A python migration handler class
    def migration_handler_cls(self):
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
    
    ##@brief Return an initialized MigrationHandler instance
    #@param ds_name str : The datasource name
    #@return A properly initialized MigrationHandler instance
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


    ##@brief Given a datasource name returns a DatasourcePlugin name
    #@param ds_name str : datasource name
    #@param ro bool : if true consider the datasource as readonly
    #@return a DatasourcePlugin name
    #@throw PluginError if datasource name not found
    #@throw DatasourcePermError if datasource is read_only but ro flag arg is
    #false
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

    ##@brief Try to fetch a datasource configuration
    #@param ds_identifier str : datasource name
    #@param ds_plugin_name : datasource plugin name
    #@return a dict containing datasource initialisation options
    #@throw NameError if a datasource plugin or instance cannot be found
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
    #@param ds_plugin_name str : datasource plugin name
    #@throw PluginError if ds_name is not an existing plugin name
    #@throw PluginTypeError if ds_name is not the name of a DatasourcePlugin
    @classmethod
    def get_datasource(cls, ds_plugin_name):
        return cls.get(ds_plugin_name).datasource_cls()
    
    ##@brief Given a plugin name returns a migration handler class
    #@param ds_plugin_name str : a datasource plugin name
    @classmethod
    def get_migration_handler(cls, ds_plugin_name):
        return cls.get(ds_plugin_name).migration_handler_cls()


##@page lodel2_datasources Lodel2 datasources
#
#@par lodel2_datasources_intro Intro
# A single lodel2 website can interact with multiple datasources. This page
# aims to describe configuration & organisation of datasources in lodel2.
# Each object is attached to a datasource. This association is done in the
# editorial model, the datasource is identified by a name.
#
#@par Datasources declaration
# To define a datasource you have to write something like this in confs file :
#<pre>
#[lodel2.datasources.DATASOURCE_NAME]
#identifier = DATASOURCE_FAMILY.SOURCE_NAME
#</pre>
# See below for DATASOURCE_FAMILY & SOURCE_NAME
#
#@par Datasources plugins
# Each datasource family is a plugin ( 
#@ref plugin_doc "More informations on plugins" ). For example mysql or a 
#mongodb plugins. Here is the CONFSPEC variable templates for datasources 
#plugin
#<pre>
#CONFSPEC = {
#                'lodel2.datasource.example.*' : {
#                    'conf1' : VALIDATOR_OPTS,
#                    'conf2' : VALIDATOR_OPTS,
#                    ...
#                }
#}
#</pre>
#MySQL example
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
#@par Configuration example
#<pre>
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
