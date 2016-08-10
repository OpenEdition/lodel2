#-*- coding: utf-8 -*-

import sys
import os.path
import importlib
import copy
from importlib.machinery import SourceFileLoader, SourcelessFileLoader

import plugins
from .exceptions import *

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
        
        ##@brief Stores the plugin module
        self.module = None
        ##@breif Stores the plugin loader module
        self.__loader_module = None
        self.__confspecs = dict()
        self.loaded = False
        
        # Importing __init__.py
        plugin_module = '%s.%s' % (VIRTUAL_PACKAGE_NAME,
                                    plugin_name)

        init_source = self.path + INIT_FILENAME
        try:
            loader = SourceFileLoader(plugin_module, init_source)
            self.module = loader.load_module()
        except (ImportError,FileNotFoundError) as e:
             raise PluginError("Failed to load plugin '%s'. It seems that the plugin name is not valid or the plugin do not exists" % plugin_name)

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

    ##@brief Browse directory to get plugin
    #@param plugin_path 
    #@return module existing
    def _discover_plugin(self, plugin_path):
        import os
        try:
            for root, dirs, files in os.walk(plugin_path, topdown = True):
                return dirs                
        except NameError:
            msg = "This plugin {plugin_path} is not valid"



    ##@brief Try to import a file from a variable in __init__.py
    #@param varname str : The variable name
    #@return loaded module
    #@throw AttributeError if varname not found
    #@throw ImportError if the file fails to be imported
    #@throw PluginError if the filename was not valid
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
    
    def loader_module(self):
        if not self.loaded:
            raise RuntimeError("Plugin %s not loaded yet."%self.name)
        return self.__loader_module

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
        from lodel.plugin.hooks import LodelHook
        LodelHook.call_hook(
            "lodel2_plugins_loaded", cls, cls._plugin_instances)
    
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

##@brief Decorator class designed to allow plugins to add custom methods
#to LeObject childs (dyncode objects)
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
    #@param return the function
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
            

##@page lodel2_plugins Lodel2 plugins system
#
# @par Plugin structure
#A plugin is  a package (a folder containing, at least, an __init__.py file.
#This file should expose multiple things :
# - a CONFSPEC variable containing configuration specifications
# - an _activate() method that returns True if the plugin can be activated (
# optionnal)
#
