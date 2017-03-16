#-*- coding: utf-8 -*-

import sys
import os.path
import importlib
import copy
import json
from importlib.machinery import SourceFileLoader

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.logger': 'logger',
    'lodel.settings.utils': ['SettingsError'],
    'lodel.plugin.hooks': ['LodelHook'],
    'lodel.plugin.exceptions': ['PluginError', 'PluginVersionError',
        'PluginTypeError', 'LodelScriptError', 'DatasourcePluginError'],
    'lodel.exceptions': ['LodelException', 'LodelExceptions',
        'LodelFatalError', 'DataNoneValid', 'FieldValidationError']})

## @package lodel.plugins Lodel2 plugins management
#@ingroup lodel2_plugins
#
# Lodel2 plugins are stored in directories
# A typicall lodel2 plugin directory structure looks like :
# - {{__init__.py}}} containing informations like full_name, authors, licence etc.
# - main.py containing hooks registration etc
# - confspec.py containing a configuration specification dictionary named CONFSPEC
#
# All plugins are expected to be found in multiple locations :
# - in the lodel package (lodel.plugins)
# - in the context directorie in a plugins/ dir (symlink to lodel.plugins) <-
#this is obsolete now, since we enforce ALL plugins to be in the lodel package
#
#@todo Check if the symlink in the lodelcontext dir is obsolete !!!
#@warning The plugins dir is at two locations : in lodel package and in
#instance directory. Some stuff seems to still needs plugins to be in
#the instance directory but it seems to be a really bad idea...

##@defgroup plugin_init_specs Plugins __init__.py specifications
#@ingroup lodel2_plugins
#@{

##@brief The package in which we will load plugins modules
VIRTUAL_PACKAGE_NAME = 'lodel.plugins'
##@brief The temporary package to import python sources
VIRTUAL_TEMP_PACKAGE_NAME = 'lodel.plugin_tmp'
##@brief Plugin init filename
INIT_FILENAME = '__init__.py' # Loaded with settings
##@brief Name of the variable containing the plugin name
PLUGIN_NAME_VARNAME = '__plugin_name__'
##@brief Name of the variable containing the plugin type
PLUGIN_TYPE_VARNAME = '__plugin_type__'
##@brief Name of the variable containing the plugin version
PLUGIN_VERSION_VARNAME = '__version__'
##@brief Name of the variable containing the confpsec filename
CONFSPEC_FILENAME_VARNAME = '__confspec__'
##@brief Name of the variable containing the confspecs
CONFSPEC_VARNAME = 'CONFSPEC'
##@brief Name of the variable containing the loader filename
LOADER_FILENAME_VARNAME = '__loader__'
##@brief Name of the variable containing the plugin dependencies
PLUGIN_DEPS_VARNAME = '__plugin_deps__'
##@brief Name of the optionnal activate method
ACTIVATE_METHOD_NAME = '_activate'
##@brief Default & failover value for plugins path list
PLUGINS_PATH = os.path.join(LodelContext.context_dir(),'plugins')

##@brief List storing the mandatory variables expected in a plugin __init__.py
#file
MANDATORY_VARNAMES = [PLUGIN_NAME_VARNAME, LOADER_FILENAME_VARNAME,
    PLUGIN_VERSION_VARNAME]

##@brief Default plugin type
DEFAULT_PLUGIN_TYPE = 'extension' #Value found in lodel/plugin/extensions.py::Extensions._type_conf_name

## @}

##@brief Describe and handle version numbers
#@ingroup lodel2_plugins
#
#A version number can be represented by a string like MAJOR.MINOR.PATCH
#or by a list [MAJOR, MINOR,PATCH ].
#
#The class implements basics comparison function and string repr
class PluginVersion(object):

    PROPERTY_LIST = ['major', 'minor', 'revision' ]

    ##@brief Version constructor
    #@param *args : You can either give a str that will be splitted on . or you
    #can give a iterable containing 3 integer or 3 arguments representing
    #major, minor and revision version
    def __init__(self, *args):
        self.__version = [0 for _ in range(3) ]
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                #Casting from string to version numbers
                spl = arg.split('.')
                invalid = False
                if len(spl) > 3:
                    raise PluginVersionError("The string '%s' is not a valid plugin \
version number" % arg)
                if len(spl) < 3:
                    spl += [ 0 for _ in range(3-len(spl))]
                try:
                    self.__version = [int(s) for s in spl]
                except (ValueError, TypeError):
                    raise PluginVersionError("The string '%s' is not a valid lodel2 \
plugin version number" % arg)
            else:
                try:
                    if len(arg) >= 1:
                        if len(arg) > 3:
                            raise PluginVersionError("Expected maximum 3 value to \
create a plugin version number but found '%s' as argument" % arg)
                        for i, v in enumerate(arg):
                            self.__version[i] = int(arg[i])
                except (TypeError, ValueError):
                    raise PluginVersionError("Unable to convert argument into plugin \
version number" % arg)
        elif len(args) > 3:
            raise PluginError("Expected between 1 and 3 positional arguments \
but %d arguments found" % len(args))
        else:
            for i,v in enumerate(args):
                self.__version[i] = int(v)
        #Checks that version numbering is correct
        for v in self.__version:
            if v < 0:
                raise PluginVersionError("No negative version number allowed !")

    ##@brief Property to access major version number
    @property
    def major(self):
        return self.__version[0]

    ##@brief Property to access minor version number
    @property
    def minor(self):
        return self.__version[1]

    ##@brief Property to access patch version number
    @property
    def revision(self):
        return self.__version[2]

    ##@brief Check and prepare comparisoon argument
    #@return A PluginVersion instance
    #@throw PluginError if invalid argument provided
    def __cmp_check(self, other):
        if not isinstance(other, PluginVersion):
            try:
                if len(other) <= 3 and len(other) > 0:
                    return PluginVersion(other)
            except TypeError:
                raise PluginError("Cannot compare argument '%s' with \
a PluginVerison instance" % other)
        return other

    ##@brief Allow accessing to versions parts using interger index
    #@param key int : index
    #@return major for key == 0, minor for key == 1, revision for key == 2
    def __getitem__(self, key):
        try:
            key = int(key)
        except (ValueError, TypeError):
            raise ValueError("Expected an int as key")
        if key < 0 or key > 2:
            raise ValueError("Key is expected to be in [0..2]")
        return self.__version[key]

    def __lt__(self, other):
        for i in range(3):
            if self[i] < other[i]:
                return True
            elif self[i] > other[i]:
                return False
        return False

    def __eq__(self, other):
        for i in range(3):
            if self[i] != other[i]:
                return False
        return True

    def __gt__(self, other):
        for i in range(3):
            if self[i] > other[i]:
                return True
            elif self[i] < other[i]:
                return False
        return False

    def __le__(self, other):
        return self < other or self == other

    def __ne__(self, other):
        return not(self == other)

    def __ge__(self, other):
        return self > other or self == other

    def __str__(self):
        return '%d.%d.%d' % tuple(self.__version)

    def __repr__(self):
        return "{'major': %d, 'minor': %d, 'revision': %d}" % tuple(
            self.__version)

##@brief Plugin metaclass that allows to "catch" child class declaration
#@ingroup lodel2_plugins
#
#Automatic script registration on child class declaration
class MetaPlugType(type):

    ##@brief Dict storing all plugin types
    #
    #key is the _type_conf_name and value is the class
    _all_ptypes = dict()

    ##@brief type constructor reimplementation
    def __init__(self, name, bases, attrs):
        #Here we can store all child classes of Plugin
        super().__init__(name, bases, attrs)
        if len(bases) == 1 and bases[0] == object:
            return
        #Regitering a new plugin type
        MetaPlugType._all_ptypes[self._type_conf_name] = self

    ##@brief Accessor to the list of plugin types
    #@return A copy of _all_ptypes attribute (a dict with typename as key
    #and the class as value)
    @classmethod
    def all_types(cls):
        return copy.copy(cls._all_ptypes)

    ##@brief Accessor to the list of plugin names
    #@return a list of plugin name
    @classmethod
    def all_ptype_names(cls):
        return list(cls._all_ptypes.keys())

    ##@brief Given a plugin type name return a Plugin child class
    #@param ptype_name str : a plugin type name
    #@return A Plugin child class
    #@throw PluginError if ptype_name is not an exsiting plugin type name
    @classmethod
    def type_from_name(cls, ptype_name):
        if ptype_name not in cls._all_ptypes:
            raise PluginError("Unknown plugin type '%s'" % ptype_name)
        return cls._all_ptypes[ptype_name]

    ##@brief Call the clear classmethod on each child classes
    @classmethod
    def clear_cls(cls):
        for pcls in cls._all_ptypes.values():
            pcls.clear_cls()


##@brief Handle plugins
#@ingroup lodel2_plugins
#
# An instance represent a loaded plugin. Class methods allow to load/preload
# plugins.
#
# Typicall Plugins load sequence is :
# 1. Settings call start method to instanciate all plugins found in confs
# 2. Settings fetch all confspecs
# 3. the loader call load_all to register hooks etc
class Plugin(object, metaclass=MetaPlugType):

    ##@brief Stores Plugin instances indexed by name
    _plugin_instances = dict()

    ##@brief Attribute used by load_all and load methods to detect circular
    #dependencies
    _load_called = []

    ##@brief Attribute that stores plugins list from discover cache file
    _plugin_list = None

    #@brief Designed to store, in child classes, the confspec indicating \
    #where plugin list is stored
    _plist_confspecs = None

    ##@brief The name of the plugin type in the confguration
    #
    #None in abstract classes and implemented by child classes
    _type_conf_name = None

    ##@brief Stores virtual modules uniq key
    #@note When testing if a dir contains a plugin, if we reimport the __init__
    #in a module with the same name, all non existing value (plugin_type for
    #example) are replaced by previous plugin values
    _mod_cnt = 0

    ##@brief Plugin class constructor
    #
    # Called by setting in early stage of lodel2 boot sequence using classmethod
    # register
    #
    # @param plugin_name str : plugin name
    # @throw PluginError
    def __init__(self, plugin_name):

        ##@brief The plugin name
        self.name = plugin_name
        ##@brief The plugin package path
        self.path = self.plugin_path(plugin_name)

        ##@brief Stores the plugin module
        self.module = None
        ##@brief Stores the plugin loader module
        self.__loader_module = None
        ##@brief The plugin confspecs
        self.__confspecs = dict()
        ##@brief Boolean flag telling if the plugin is loaded or not
        self.loaded = False

        # Importing __init__.py infos in it
        plugin_module = self.module_name()
        self.module = LodelContext.module(plugin_module)

        # loading confspecs
        try:
            # Loading confspec directly from __init__.py
            self.__confspecs = getattr(self.module, CONFSPEC_VARNAME)
        except AttributeError:
            # Loading file in __confspec__ var in __init__.py
            try:
                module = self._import_from_init_var(CONFSPEC_FILENAME_VARNAME)
            except AttributeError:
                msg = "Malformed plugin {plugin} . No {varname} not {filevar} found in __init__.py"
                msg = msg.format(
                    plugin = self.name,
                    varname = CONFSPEC_VARNAME,
                    filevar = CONFSPEC_FILENAME_VARNAME)
                raise PluginError(msg)
            except ImportError as e:
                msg = "Broken plugin {plugin} : {expt}"
                msg = msg.format(
                    plugin = self.name,
                    expt = str(e))
                raise PluginError(msg)
            except Exception as e:
                msg = "Plugin '%s' :"+str(e)
                raise e.__class__(msg)

            try:
                # loading confpsecs from file
                self.__confspecs = getattr(module, CONFSPEC_VARNAME)
            except AttributeError:
                msg = "Broken plugin. {varname} not found in '{filename}'"
                msg = msg.format(
                    varname = CONFSPEC_VARNAME,
                    filename = confspec_filename)
                raise PluginError(msg)
        # loading plugin version
        try:
            #this try block should be useless. The existance of
            #PLUGIN_VERSION_VARNAME in init file is mandatory
            self.__version = getattr(self.module, PLUGIN_VERSION_VARNAME)
        except AttributeError:
            msg = "Error that should not append while loading plugin '%s': no \
%s found in plugin init file. Malformed plugin"
            msg %= (plugin_name, PLUGIN_VERSION_VARNAME)
            raise LodelFatalError(msg)

        # Load plugin type
        try:
            self.__type = getattr(self.module, PLUGIN_TYPE_VARNAME)
        except AttributeError:
            self.__type = DEFAULT_PLUGIN_TYPE
        self.__type = str(self.__type).lower()
        if self.__type not in MetaPlugType.all_ptype_names():
            raise PluginError("Unknown plugin type '%s'" % self.__type)
        # Load plugin name from init file (just for checking)
        try:
            #this try block should be useless. The existance of
            #PLUGIN_NAME_VARNAME in init file is mandatory
            pname = getattr(self.module, PLUGIN_NAME_VARNAME)
        except AttributeError:
            msg = "Error that should not append : no %s found in plugin \
init file. Malformed plugin"
            msg %= PLUGIN_NAME_VARNAME
            raise LodelFatalError(msg)
        if pname != plugin_name:
            msg = "Plugin's discover cache inconsistency detected ! Cached \
name differ from the one found in plugin's init file"
            raise PluginError(msg)

    ##@brief Try to import a file from a variable in __init__.py
    #@param varname str : The variable name
    #@return loaded module
    #@throw AttributeError if varname not found
    #@throw ImportError if the file fails to be imported
    #@throw PluginError if the filename was not valid
    #@todo Some strange things append :
    #when loading modules in test self.module.__name__ does not contains
    #the package... but in prod cases the self.module.__name__ is
    #the module fullname... Just a reminder note to explain the dirty
    #if on self_modname
    def _import_from_init_var(self, varname):
        # Read varname
        try:
            filename = getattr(self.module, varname)
        except AttributeError:
            msg = "Malformed plugin {plugin}. No {varname} found in __init__.py"
            msg = msg.format(
                plugin = self.name,
                varname = LOADER_FILENAME_VARNAME)
            raise PluginError(msg)
        #Path are not allowed
        if filename != os.path.basename(filename):
            msg = "Invalid {varname} content : '{fname}' for plugin {name}"
            msg = msg.format(
                varname=varname,
                fname=filename,
                name=self.name)
            raise PluginError(msg)
        #See the todo
        if len(self.module.__name__.split('.')) == 1:
            self_modname = self.module.__package__
        else:
            self_modname = self.module.__name__
        #extract module name from filename
        base_mod = '.'.join(filename.split('.')[:-1])
        module_name = self_modname+"."+base_mod
        return importlib.import_module(module_name)

    ##@brief Return associated module name
    def module_name(self):
        path_array = self.path.split('/')
        if 'plugins' not in self.path:
            raise PluginError("Bad path for plugin %s : %s" % (
                self.name, self.path))
        return '.'.join(['lodel'] + path_array[path_array.index('plugins'):])

    ##@brief Check dependencies of plugin
    #@return A list of plugin name to be loaded before
    def check_deps(self):
        try:
            res = getattr(self.module, PLUGIN_DEPS_VARNAME)
        except AttributeError:
            return list()
        result = list()
        errors = list()
        for plugin_name in res:
            try:
                result.append(self.get(plugin_name))
            except PluginError:
                errors.append(plugin_name)
        if len(errors) > 0:
            raise PluginError(  "Bad dependencie for '%s' :"%self.name,
                                ', '.join(errors))
        return result

    ##@brief Check if the plugin should be activated
    #
    #Try to fetch a function called @ref ACTIVATE_METHOD_NAME in __init__.py
    #of a plugin. If none found assert that the plugin can be loaded, else
    #the method is called. If it returns anything else that True, the plugin
    #is noted as not activable
    #
    # @note Maybe we have to exit everything if a plugin cannot be loaded...
    def activable(self):
        try:
            test_fun = getattr(self.module, ACTIVATE_METHOD_NAME)
        except AttributeError:
            msg = "No %s method found for plugin %s. Assuming plugin is ready to be loaded"
            msg %= (ACTIVATE_METHOD_NAME, self.name)
            logger.debug(msg)
            test_fun = lambda:True
        return test_fun()

    ##@brief Load a plugin
    #
    #Loading a plugin means importing a file. The filename is defined in the
    #plugin's __init__.py file in a LOADER_FILENAME_VARNAME variable.
    #
    #The loading process has to take care of other things :
    #- loading dependencies (other plugins)
    #- check that the plugin can be activated using Plugin.activate() method
    #- avoid circular dependencies infinite loop
    def _load(self):
        if self.loaded:
            return
        #Test that plugin "wants" to be activated
        activable = self.activable()
        if not(activable is True):
            msg = "Plugin %s is not activable : %s"
            msg %= (self.name, activable)
            raise PluginError(msg)

        #Circular dependencie detection
        if self.name in self._load_called:
            raise PluginError("Circular dependencie in Plugin detected. Abording")
        else:
            self._load_called.append(self.name)

        #Dependencie load
        for dependencie in self.check_deps():
            activable = dependencie.activable()
            if activable is True:
                dependencie._load()
            else:
                msg = "Plugin {plugin_name} not activable because it depends on plugin {dep_name} that is not activable : {reason}"
                msg = msg.format(
                    plugin_name = self.name,
                    dep_name = dependencie.name,
                    reason = activable)

        #Loading the plugin
        try:
            self.__loader_module = self._import_from_init_var(LOADER_FILENAME_VARNAME)
        except PluginError as e:
            raise e
        except ImportError as e:
            msg = "Broken plugin {plugin} : {expt}"
            msg = msg.format(
                plugin = self.name,
                expt = str(e))
            raise PluginError(msg)
        logger.debug("Plugin '%s' loaded" % self.name)
        self.loaded = True

    ##@brief Returns the loader module
    #
    #Accessor for the __loader__ python module
    def loader_module(self):
        if not self.loaded:
            raise RuntimeError("Plugin %s not loaded yet."%self.name)
        return self.__loader_module

    def __str__(self):
        return "<LodelPlugin '%s' version %s>" % (self.name, self.__version)

    ##@brief Call load method on every pre-loaded plugins
    #
    # Called by loader to trigger hooks registration.
    # This method have to avoid circular dependencies infinite loops. For this
    # purpose a class attribute _load_called exists.
    # @throw PluginError
    @classmethod
    def load_all(cls):
        errors = dict()
        cls._load_called = []
        for name, plugin in cls._plugin_instances.items():
            try:
                plugin._load()
            except PluginError as e:
                errors[name] = e
        if len(errors) > 0:
            msg = "Errors while loading plugins :"
            for name, e in errors.items():
                msg += "\n\t%20s : %s" % (name,e)
            msg += "\n"
            raise PluginError(msg)
        LodelHook.call_hook(
            "lodel2_plugins_loaded", cls, cls._plugin_instances)


    ##@return a copy of __confspecs attr
    @property
    def confspecs(self):
        return copy.copy(self.__confspecs)

    ##@brief Accessor to confspec indicating where we can find the plugin list
    #@note Abtract method implemented only for Plugin child classes
    #This attribute indicate where we fetch the plugin list.
    @classmethod
    def plist_confspecs(cls):
        if cls._plist_confspecs is None:
            raise LodelFatalError('Unitialized _plist_confspecs attribute for \
%s' % cls.__name__)
        return copy.copy(cls._plist_confspecs)

    ##@brief Retrieves plugin list confspecs
    #
    #This method ask for each Plugin child class the confspecs specifying where
    #the wanted plugin list is stored. (For example DatasourcePlugin expect
    #that a list of ds plugin to load stored in lodel2 section, datasources key
    # etc...
    @classmethod
    def plugin_list_confspec(cls):
        LodelContext.expose_modules(globals(), {
            'lodel.settings.validator': ['confspec_append']})
        res = dict()
        for pcls in cls.plugin_types():
            plcs = pcls.plist_confspec()
            confspec_append(res, plcs)
        return res

    ##@brief Register a new plugin
    #
    #@param plugin_name str : The plugin name
    #@return a Plugin instance
    #@throw PluginError
    @classmethod
    def register(cls, plugin_name):
        if plugin_name in cls._plugin_instances:
            msg = "Plugin allready registered with same name %s"
            msg %= plugin_name
            raise PluginError(msg)
        #Here we check that previous discover found a plugin with that name
        pdcache = cls.discover()
        if plugin_name not in pdcache:
            raise PluginError("No plugin named '%s' found" % plugin_name)
        ptype = pdcache[plugin_name]['type']
        pcls = MetaPlugType.type_from_name(ptype)
        plugin = pcls(plugin_name)
        cls._plugin_instances[plugin_name] = plugin
        logger.debug("Plugin %s available." % plugin)
        return plugin

    ##@brief Plugins instances accessor
    #
    #@param plugin_name str: The plugin name
    #@return a Plugin instance
    #@throw PluginError if plugin not found
    @classmethod
    def get(cls, plugin_name):
        try:
            return cls._plugin_instances[plugin_name]
        except KeyError:
            msg = "No plugin named '%s' loaded"
            msg %= plugin_name
            raise PluginError(msg)

    ##@brief Given a plugin name returns the plugin path
    # @param plugin_name str : The plugin name
    # @return the plugin directory path
    @classmethod
    def plugin_path(cls, plugin_name):
        plist = cls.plugin_list()
        if plugin_name not in plist:
            raise PluginError("No plugin named '%s' found" % plugin_name)

        try:
            return cls.get(plugin_name).path
        except PluginError:
            pass

        return plist[plugin_name]['path']

    ##@brief Return the plugin module name
    #
    #This module name is the "virtual" module where we imported the plugin.
    #
    #Typically composed like VIRTUAL_PACKAGE_NAME.PLUGIN_NAME
    #@warning Brokes subdire feature
    #@param plugin_name str : a plugin name
    #@return a string representing a module name
    #@todo fix broken subdir capabilitie ( @see module_name() )
    #@todo check if used, else delete it
    @classmethod
    def plugin_module_name(cls, plugin_name):
        return "%s.%s" % (VIRTUAL_PACKAGE_NAME, plugin_name)

    ##@brief Start the Plugin class
    #
    # Called by Settings.__bootstrap()
    #
    # This method load path and preload plugins
    @classmethod
    def start(cls, plugins):
        for plugin_name in plugins:
            cls.register(plugin_name)

    ##@brief Attempt to "restart" the Plugin class
    @classmethod
    def clear(cls):
        if cls._plugin_instances != dict():
            cls._plugin_instances = dict()
        if cls._load_called != []:
            cls._load_called = []
        MetaPlugType.clear_cls()

    ##@brief Designed to be implemented by child classes
    @classmethod
    def clear_cls(cls):
        pass

    ##@brief Reccursively walk throught paths to find plugin, then stores
    #found plugin in a static var
    #
    #Found plugins are stored in cls._plugin_list
    #@note The discover is run only if no cached datas are found
    #@return a list of dict with plugin infos { see @ref _discover }
    #@todo add max_depth and no symlink following feature
    @classmethod
    def discover(cls):
        if cls._plugin_list is not None:
            return cls._plugin_list
        logger.info("Running plugin discover")
        tmp_res = cls._discover(PLUGINS_PATH)
        #Formating and dedoubloning result
        result = dict()
        for pinfos in tmp_res:
            pname = pinfos['name']
            if (    pname in result
                    and pinfos['version'] > result[pname]['version'])\
                or pname not in result:
                result[pname] = pinfos
            else:
                #dropped
                pass
        cls._plugin_list = result
        return result

    ##@brief Return discover result
    #@param refresh bool : if true invalidate all plugin list cache
    #@note If discover cache file not found run discover first
    #@note if refresh is set to True discover MUST have been run at least
    #one time. In fact refresh action load the list of path to explore
    #from the plugin's discover cache
    @classmethod
    def plugin_list(cls, refresh = False):
        return cls._plugin_list

    ##@brief Return a list of child Class Plugin
    @classmethod
    def plugin_types(cls):
        return MetaPlugType.all_types()

    ##@brief Check if a directory is a plugin module
    #@param path str : path to check
    #@param assert_in_package bool : if False didn't check that path is
    #a subdir of PLUGINS_PATH
    #@return a dict with name, version and path if path is a plugin module, else False
    @classmethod
    def dir_is_plugin(cls, path, assert_in_package = True):
        log_msg = "%s is not a plugin directory because : " % path
        if assert_in_package:
            #Check that path is a subdir of PLUGINS_PATH
            abspath = os.path.abspath(path)
            if not abspath.startswith(os.path.abspath(PLUGINS_PATH)):
                raise PluginError(
                    "%s is not a subdir of %s" % log_msg, PLUGINS_PATH)
        #Checks that path exists
        if not os.path.isdir(path):
            raise ValueError(
                "Expected path to be a directory, but '%s' found" % path)
        #Checks that path contains plugin's init file
        initfile = os.path.join(path, INIT_FILENAME)
        if not os.path.isfile(initfile):
            log_msg += "'%s' not found" % (INIT_FILENAME)
            logger.debug(log_msg)
            return False
        #Importing plugin's init file to check contained datas
        try:
            initmod, modname = cls.import_init(path)
        except PluginError as e:
            log_msg += "unable to load '%s'. Exception raised : %s"
            log_msg %= (INIT_FILENAME, e)
            logger.debug(log_msg)
            return False
        #Checking mandatory init module variables
        for attr_name in MANDATORY_VARNAMES:
            if not hasattr(initmod,attr_name):
                log_msg += " mandatory variable '%s' not found in '%s'"
                log_msg %= (attr_name, INIT_FILENAME)
                logger.debug(log_msg)
                return False
        #Fetching plugin's version
        try:
            pversion = getattr(initmod, PLUGIN_VERSION_VARNAME)
        except (NameError, AttributeError) as e:
            msg = "Invalid plugin version found in %s : %s"
            msg %= (path, e)
            raise PluginError(msg)
        #Fetching plugin's type
        try:
            ptype = getattr(initmod, PLUGIN_TYPE_VARNAME)
        except (NameError, AttributeError) as e:
            ptype = DEFAULT_PLUGIN_TYPE
        pname = getattr(initmod, PLUGIN_NAME_VARNAME)
        return {'name': pname,
            'version': PluginVersion(pversion),
            'path': path,
            'type': ptype}

    ##@brief Import init file from a plugin path
    #@param path str : Directory path
    #@return a tuple (init_module, module_name)
    #@todo replace by LodelContext usage !!! (not mandatory, this fun
    #is only used in plugin discover method)
    @classmethod
    def import_init(cls, path):
        cls._mod_cnt += 1 # in order to ensure module name unicity
        init_source = os.path.join(path, INIT_FILENAME)
        temp_module = '%s.%s.%s%d' % (
            VIRTUAL_TEMP_PACKAGE_NAME, os.path.basename(os.path.dirname(path)),
            'test_init', cls._mod_cnt)
        try:
            loader = SourceFileLoader(temp_module, init_source)
        except (ImportError, FileNotFoundError) as e:
            raise PluginError("Unable to import init file from '%s' : %s" % (
                temp_module, e))
        try:
            res_module = loader.load_module()
        except Exception as e:
            raise PluginError("Unable to import initfile : %s" % e)
        return (res_module, temp_module)

    @classmethod
    def debug_wrapper(cls, updglob = None):
        if updglob is not None:
            for k, v in updglob.items():
                globals()[k] = v
        print(logger)

    ##@brief Reccursiv plugin discover given a path
    #@param path str : the path to walk through
    #@return A dict with plugin_name as key and {'path':..., 'version':...} as value
    @classmethod
    def _discover(cls, path):
        #Ensure plugins symlink creation
        LodelContext.expose_modules(globals(), {
            'lodel.plugins': 'plugins'})
        res = []
        to_explore = [path]
        while len(to_explore) > 0:
            cur_path = to_explore.pop()
            for f in os.listdir(cur_path):
                f_path = os.path.join(cur_path, f)
                if f not in ['.', '..'] and os.path.isdir(f_path):
                    #Check if it is a plugin directory
                    test_result = cls.dir_is_plugin(f_path)
                    if not (test_result is False):
                        logger.info("Plugin '%s' found in %s" % (
                            test_result['name'],f_path))
                        res.append(test_result)
                    else:
                        to_explore.append(f_path)
        return res

def debug_wrapper_mod():
    print("MOD : ",logger)

##@brief Decorator class designed to allow plugins to add custom methods
#to LeObject childs (dyncode objects)
#@ingroup lodel2_plugins
#
class CustomMethod(object):
    ##@brief Stores registered custom methods
    #
    #Key = LeObject child class name
    #Value = CustomMethod instance
    _custom_methods = dict()

    INSTANCE_METHOD = 0
    CLASS_METHOD = 1
    STATIC_METHOD = 2

    ##@brief Decorator constructor
    #@param component_name str : the name of the component to enhance
    #@param method_name str : the name of the method to inject (if None given
    #@param method_type int : take value in one of
    #CustomMethod::INSTANCE_METHOD CustomMethod::CLASS_METHOD or
    #CustomMethod::STATIC_METHOD
    #use the function name
    def __init__(self, component_name, method_name = None, method_type=0):
        ##@brief The targeted LeObject child class
        self._comp_name = component_name
        ##@brief The method name
        self._method_name = method_name
        ##@brief The function (that will be the injected method)
        self._fun = None
        ##@brief Stores the type of method (instance, class or static)
        self._type = int(method_type)
        if self._type not in (self.INSTANCE_METHOD, self.CLASS_METHOD,\
            self.STATIC_METHOD):
            raise ValueError("Excepted value for method_type was one of \
CustomMethod::INSTANCE_METHOD CustomMethod::CLASS_METHOD or \
CustomMethod::STATIC_METHOD, but got %s" % self._type)

    ##@brief called just after __init__
    #@param fun function : the decorated function
    def __call__(self, fun):
        if self._method_name is None:
            self._method_name = fun.__name__
        if self._comp_name not in self._custom_methods:
            self._custom_methods[self._comp_name] = list()

        if self._method_name in [ scm._method_name for scm in self._custom_methods[self._comp_name]]:
            raise RuntimeError("A method named %s allready registered by \
another plugin : %s" % (
                self._method_name,
                self._custom_methods[self._comp_name].__module__))
        self._fun = fun
        self._custom_methods[self._comp_name].append(self)

    ##@brief Textual representation
    #@return textual representation of the CustomMethod instance
    def __repr__(self):
        res = "<CustomMethod name={method_name} target={classname} \
source={module_name}.{fun_name}>"
        return res.format(
            method_name = self._method_name,
            classname = self._comp_name,
            module_name = self._fun.__module__,
            fun_name = self._fun.__name__)

    ##@brief Return a well formed method
    #
    #@note the type of method depends on the _type attribute
    #@return a method directly injectable in the target class
    def __get_method(self):
        if self._type == self.INSTANCE_METHOD:
            def custom__get__(self, obj, objtype = None):
                return types.MethodType(self, obj, objtype)
            setattr(self._fun, '__get__', custom__get__)
            return self._fun
        elif self._type == self.CLASS_METHOD:
            return classmethod(self._fun)
        elif self._type == self.STATIC_METHOD:
            return staticmethod(self._fun)
        else:
            raise RuntimeError("Attribute _type is not one of \
CustomMethod::INSTANCE_METHOD CustomMethod::CLASS_METHOD \
CustomMethod::STATIC_METHOD")

    ##@brief Handle custom method dynamic injection in LeAPI dyncode
    #
    #Called by lodel2_dyncode_loaded hook defined at
    #lodel.plugin.core_hooks.lodel2_plugin_custom_methods()
    #
    #@param cls
    #@param dynclasses LeObject child classes : List of dynamically generated
    #LeObject child classes
    @classmethod
    def set_registered(cls, dynclasses):
        from lodel import logger
        dyn_cls_dict = { dc.__name__:dc for dc in dynclasses}
        for cls_name, custom_methods in cls._custom_methods.items():
            for custom_method in custom_methods:
                if cls_name not in dyn_cls_dict:
                    logger.error("Custom method %s adding fails : No dynamic \
LeAPI objects named %s." % (custom_method, cls_name))
                elif custom_method._method_name in dir(dyn_cls_dict[cls_name]):
                    logger.warning("Overriding existing method '%s' on target \
with %s" % (custom_method._method_name, custom_method))
                else:
                    setattr(
                        dyn_cls_dict[cls_name],
                        custom_method._method_name,
                        custom_method.__get_method())
                    logger.debug(
                        "Custom method %s added to target" % custom_method)

def wrapper_debug_fun():
    print(logger)
