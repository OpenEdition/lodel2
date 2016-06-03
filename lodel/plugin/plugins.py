#-*- coding: utf-8 -*-

import sys
import os.path
import importlib
import copy
from importlib.machinery import SourceFileLoader, SourcelessFileLoader

import plugins

## @package lodel.plugins Lodel2 plugins management
#
# Lodel2 plugins are stored in directories
# A typicall lodel2 plugin directory structure looks like :
# - {{__init__.py}}} containing informations like full_name, authors, licence etc.
# - main.py containing hooks registration etc
# - confspec.py containing a configuration specification dictionary named CONFSPEC

##@brief The package in which we will load plugins modules
VIRTUAL_PACKAGE_NAME = 'lodel.plugins'
INIT_FILENAME = '__init__.py' # Loaded with settings
CONFSPEC_FILENAME_VARNAME = '__confspec__'
CONFSPEC_VARNAME = 'CONFSPEC'
LOADER_FILENAME_VARNAME = '__loader__'
PLUGIN_DEPS_VARNAME = '__plugin_deps__'
ACTIVATE_METHOD_NAME = '_activate'

class PluginError(Exception):
    pass

##@brief Handle plugins
#
# An instance represent a loaded plugin. Class methods allow to load/preload
# plugins.
#
# Typicall Plugins load sequence is :
# 1. Settings call start method to instanciate all plugins found in confs
# 2. Settings fetch all confspecs
# 3. the loader call load_all to register hooks etc
class Plugin(object):
    
    ##@brief Stores plugin directories paths
    _plugin_directories = None
    
    ##@brief Stores Plugin instances indexed by name
    _plugin_instances = dict()
    
    ##@brief Attribute used by load_all and load methods to detect circular
    #dependencies
    _load_called = []

    ##@brief Plugin class constructor
    #
    # Called by setting in early stage of lodel2 boot sequence using classmethod
    # register
    #
    # @param plugin_name str : plugin name
    # @throw PluginError
    def __init__(self, plugin_name):
        self.started()
        self.name = plugin_name
        self.path = self.plugin_path(plugin_name)

        self.module = None
        self.__confspecs = dict()
        self.loaded = False
        
        # Importing __init__.py
        plugin_module = '%s.%s' % (VIRTUAL_PACKAGE_NAME,
                                    plugin_name)

        init_source = self.path + INIT_FILENAME
        try:
            loader = SourceFileLoader(plugin_module, init_source)
            self.module = loader.load_module()
        except ImportError as e:
             raise PluginError("Failed to load plugin '%s'. It seems that the plugin name is not valid" % plugin_name)

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

            try:
                # loading confpsecs from file
                self.__confspecs = getattr(module, CONFSPEC_VARNAME)
            except AttributeError:
                msg = "Broken plugin. {varname} not found in '{filename}'"
                msg = msg.format(
                    varname = CONFSPEC_VARNAME,
                    filename = confspec_filename)
                raise PluginError(msg)

    ##@brief Try to import a file from a variable in __init__.py
    #@param varname str : The variable name
    #@throw AttributeError if varname not found
    #@throw ImportError if the file fails to be imported
    #@throw PluginError if the filename was not valid
    def _import_from_init_var(self, varname):
        # Read varname
        filename = getattr(self.module, varname)
        #Path are not allowed
        if filename != os.path.basename(filename):
            msg = "Invalid {varname} content : '{fname}' for plugin {name}"
            msg = msg.format(
                varname = varname,
                fname = filename,
                name = self.name)
            raise PluginError(msg)
        # importing the file in varname
        module_name = self.module.__name__+"."+varname
        filename = self.path + filename
        loader = SourceFileLoader(module_name, filename)
        return loader.load_module()
    
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
        from lodel import logger
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
        from lodel import logger
        #Test that plugin "wants" to be activated
        activable = self.activable()
        if not(activable is True):
            msg = "Plugin %s is not activable : %s"
            msg %= (self.name, activable)
            raise PluginError(activable)

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
            self._import_from_init_var(LOADER_FILENAME_VARNAME)
        except AttributeError:
            msg = "Malformed plugin {plugin}. No {varname} found in __init__.py"
            msg = msg.format(
                plugin = self.name,
                varname = LOADER_FILENAME_VARNAME)
            raise PluginError(msg)
        except ImportError as e:
            msg = "Broken plugin {plugin} : {expt}"
            msg = msg.format(
                plugin = self.name,
                expt = str(e))
            raise PluginError(msg)
        logger.debug("Plugin '%s' loaded" % self.name)
        self.loaded = True
             
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
    
    ##@return a copy of __confspecs attr
    @property
    def confspecs(self):
        return copy.copy(self.__confspecs)

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
        plugin = cls(plugin_name)
        cls._plugin_instances[plugin_name] = plugin
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
        cls.started()
        try:
            return cls.get(plugin_name).path
        except PluginError:
            pass
        
        path = None
        for cur_path in cls._plugin_directories:
            plugin_path = os.path.join(cur_path, plugin_name)+'/'
            if os.path.isdir(plugin_path):
                return plugin_path
        raise NameError("No plugin named '%s'" % plugin_name)

    @classmethod
    def plugin_module_name(cls, plugin_name):
        return "%s.%s" % (VIRTUAL_PACKAGE_NAME, plugin_name)

    ##@brief Start the Plugin class
    # 
    # Called by Settings.__bootstrap()
    #
    # This method load path and preload plugins
    @classmethod
    def start(cls, plugins_directories, plugins):
        if cls._plugin_directories is not None:
            return
        import inspect
        self_path = inspect.getsourcefile(Plugin)
        default_plugin_path = os.path.abspath(self_path + '../../../../plugins')
        if plugins_directories is None:
            plugins_directories = list()
        plugins_directories += [ default_plugin_path ]
        cls._plugin_directories = list(set(plugins_directories))
        for plugin_name in plugins:
            cls.register(plugin_name)
        
    @classmethod
    def started(cls, raise_if_not = True):
        res = cls._plugin_directories is not None
        if raise_if_not and not res:
            raise RuntimeError("Class Plugins is not initialized")
            
    @classmethod
    def clear(cls):
        if cls._plugin_directories is not None:
            cls._plugin_directories = None
        if cls._plugin_instances != dict():
            cls._plugin_instances = dict()
        if cls._load_called != []:
            cls._load_called = []

##@page lodel2_plugins Lodel2 plugins system
#
# @par Plugin structure
#A plugin is  a package (a folder containing, at least, an __init__.py file.
#This file should expose multiple things :
# - a CONFSPEC variable containing configuration specifications
# - an _activate() method that returns True if the plugin can be activated (
# optionnal)
#
