#-*- coding: utf-8 -*-

import os.path

from importlib.machinery import SourceFileLoader, SourcelessFileLoader

## @package lodel.plugins Lodel2 plugins management
#
# Lodel2 plugins are stored in directories
# A typicall lodel2 plugin directory structure looks like :
# - {{__init__.py}}} containing informations like full_name, authors, licence etc.
# - main.py containing hooks registration etc
# - confspec.py containing a configuration specification dictionary named CONFSPEC

##@brief The package in wich we will load plugins modules
VIRTUAL_PACKAGE_NAME = 'lodel.plugins_pkg'
CONFSPEC_FILENAME = 'confspec.py'
MAIN_FILENAME = 'main.py'
CONFSPEC_VARNAME = 'CONFSPEC'

class PluginError(Exception):
    pass

class Plugins(object):
    
    ##@brief Stores plugin directories paths
    _plugin_directories = None
    ##@brief Optimisation cache storage for plugin paths
    _plugin_paths = dict()

    def __init__(self): # may be useless
        self.started()
    
    ##@brief Given a plugin name returns the plugin path
    # @param plugin_name str : The plugin name
    # @return the plugin directory path
    @classmethod
    def plugin_path(cls, plugin_name):
        cls.started()
        try:
            return cls._plugin_paths[plugin_name]
        except KeyError:
            pass
        
        path = None
        for cur_path in cls._plugin_directories:
            plugin_path = os.path.join(cur_path, plugin_name)+'/'
            if os.path.isdir(plugin_path):
                return plugin_path
        raise NameError("No plugin named '%s'" % plugin_name)

    ##@brief Fetch a confspec given a plugin_name
    # @param plugin_name str : The plugin name
    # @return a dict of conf spec
    # @throw PluginError if plugin_name is not valid
    @classmethod
    def get_confspec(cls, plugin_name):
        cls.started()
        plugin_path = cls.plugin_path(plugin_name)
        plugin_module = '%s.%s' % ( VIRTUAL_PACKAGE_NAME,
                                    plugin_name)
        conf_spec_module = plugin_module + '.confspec'
        
        conf_spec_source = plugin_path + CONFSPEC_FILENAME
        try:
            loader = SourceFileLoader(conf_spec_module, conf_spec_source)
            confspec_module = loader.load_module()
        except ImportError:
            raise PluginError("Failed to load plugin '%s'. It seems that the plugin name is not valid" % plugin_name)
        return getattr(confspec_module, CONFSPEC_VARNAME)
 
    ##@brief Load a module to register plugin's hooks
    # @param plugin_name str : The plugin name
    @classmethod
    def load_plugin(cls, plugin_name):
        cls.started()
        plugin_path = cls.plugin_path(plugin_name)
        plugin_module = '%s.%s' % ( VIRTUAL_PACKAGE_NAME,
                                    plugin_name)
        main_module = plugin_module + '.main'
        main_source = plugin_path + MAIN_FILENAME
        try:
            loader = SourceFileLoader(main_module, main_source)
            main_module = loader.load_module()
        except ImportError:
            raise PluginError("Failed to load plugin '%s'. It seems that the plugin name is not valid" % plugin_name)
        
    ##@brief Bootstrap the Plugins class
    @classmethod
    def bootstrap(cls, plugins_directories):
        from lodel.settings import Settings
        cls.start(Settings.plugins_path)
    
    ##@brief Start the Plugins class by explicitly giving a plugin directory path
    # @param plugins_directories list : List of path
    @classmethod
    def start(cls, plugins_directories):
        import inspect
        self_path = inspect.getsourcefile(Plugins)
        default_plugin_path = os.path.abspath(self_path + '../../../../plugins')
        if plugins_directories is None:
            plugins_directories = list()
        plugins_directories += [ default_plugin_path ]
        cls._plugin_directories = list(set(plugins_directories))
        

    @classmethod
    def started(cls, raise_if_not = True):
        res = cls._plugin_directories is not None
        if raise_if_not and not res:
            raise RuntimeError("Class Plugins is not initialized")
