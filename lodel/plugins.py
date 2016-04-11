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

VIRTUAL_PACKAGE_NAME = 'lodel.plugins_pkg'
CONFSPEC_NAME = 'confspec.py'

class Plugins(object):
    
    ## @brief Stores plugin directories paths
    _plugin_directories = None
    ## @brief Optimisation cache storage for plugin paths
    _plugin_paths = dict()

    def __init__(self):
        self.started()
    
    ## @brief Given a plugin name returns the plugin path
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
            print(plugin_path)
            if os.path.isdir(plugin_path):
                return plugin_path
        raise NameError("No plugin named '%s'" % plugin_name)

    ## @brief Fetch a confspec given a plugin_name
    # @param plugin_name str : The plugin name
    # @return a dict of conf spec
    @classmethod
    def get_confspec(cls, plugin_name):
        cls.started()
        plugin_path = cls.plugin_path(plugin_name)
        plugin_module = '%s.%s' % ( VIRTUAL_PACKAGE_NAME,
                                    plugin_name)
        conf_spec_module = plugin_module + '.confspec'
        
        conf_spec_source = plugin_path + CONFSPEC_NAME

        loader = SourceFileLoader(conf_spec_module, conf_spec_source)
        confspec_module = loader.load_module()
        return getattr(confspec_module, 'CONFSPEC')

    @classmethod
    def bootstrap(cls, plugins_directories):
        cls._plugin_directories = plugins_directories

    @classmethod
    def started(cls, raise_if_not = True):
        res = cls._plugin_directories is not None
        if raise_if_not and not res:
            raise RuntimeError("Class Plugins is not initialized")
