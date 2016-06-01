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

##@brief The package in wich we will load plugins modules
VIRTUAL_PACKAGE_NAME = 'lodel.plugins'
INIT_FILENAME = '__init__.py' # Loaded with settings
CONFSPEC_FILENAME_VARNAME = '__confspec__'
CONFSPEC_VARNAME = 'CONFSPEC'
LOADER_FILENAME_VARNAME = '__loader__'

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

    _plugin_instances = dict()

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
        
        # Importing __init__.py
        plugin_module = '%s.%s' % ( VIRTUAL_PACKAGE_NAME,
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

    ##@brief Register hooks etc
    def load(self):
        from lodel import logger
        try:
            return self._import_from_init_var(LOADER_FILENAME_VARNAME)
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
                
    @classmethod
    def load_all(cls):
        errors = dict()
        for name, plugin in cls._plugin_instances.items():
            try:
                plugin.load()
            except PluginError as e:
                errors[name] = e
        if len(errors) > 0:
            msg = "Errors while loading plugins :"
            for name, e in errors.items():
                msg += "\n\t%20s : %s" % (name,e)
            msg += "\n"
            raise PluginError(msg)

    @property
    def confspecs(self):
        return copy.copy(self.__confspecs)

    ##@brief Register a new plugin
    # 
    # preload
    @classmethod
    def register(cls, plugin_name):
        if plugin_name in cls._plugin_instances:
            msg = "Plugin allready registered with same name %s"
            msg %= plugin_name
            raise PluginError(msg)
        plugin = cls(plugin_name)
        cls._plugin_instances[plugin_name] = plugin
        return plugin

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

##@page lodel2_plugins Lodel2 plugins system
#
# @par Plugin structure
#A plugin is  a package (a folder containing, at least, an __init__.py file.
#This file should expose multiple things :
# - a CONFSPEC variable containing configuration specifications
# - an _activate() method that returns True if the plugin can be activated (
# optionnal)
#
