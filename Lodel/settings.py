#-*- coding: utf-8 -*-

import types
import warnings
from . import settings_format

## @package Lodel.settings
#
# @brief Defines stuff to handles Lodel2 configuration (see @ref lodel_settings )
#
# To access the confs use the Lodel.settings.Settings SettingsHandler instance

## @brief A class designed to handles Lodel2 settings
#
# When instanciating a SettingsHandler, the new instance is filled with the content of settings.py (in the root directory of lodel2
#
# @warning You don't have to instanciate this class, you can access to the global instance with the Settings variable in this module
# @todo Forbid module assignement in settings ! and disable tests about this
# @todo Implements a type checking of config value
# @todo Implements default values for config keys
class SettingsHandler(object):
    
    ## @brief Shortcut
    _allowed = settings_format.ALLOWED + settings_format.MANDATORY
    ## @brief Shortcut
    _mandatory = settings_format.MANDATORY

    def __init__(self):
        try:
            import settings as default_settings
            self._load_module(default_settings)
        except ImportError:
            warnings.warn("Unable to find global default settings")

        ## @brief A flag set to True when the instance is fully loaded
        self._set_loaded(False if len(self._missings()) > 0 else True)
    
    ## @brief Compat wrapper for getattr
    def get(self, name):
        return getattr(self, name)
    
    ## @brief Compat wrapper for setattr
    def set(self, name, value):
        return setattr(self, name, value)

    ## @brief Load every module properties in the settings instance
    #
    # Load a module content into a SettingsHandler instance and checks that no mandatory settings are missing
    # @note Example : <pre> import my_cool_settings;
    # Settings._load_module(my_cool_settings);</pre>
    # @param module module|None: a loaded module (if None just check for missing settings)
    # @throw LookupError if invalid settings found or if mandatory settings are missing
    def load_module(self, module = None):
        if not(module is None):
            self._load_module(module)
        missings = self._missings()
        if len(missings) > 0:
            self._loaded = False
            raise LookupError("Mandatory settings are missing : %s"%missings)
        self._set_loaded(True)
    
    ## @brief supersede of default __setattr__ method
    def __setattr__(self, name, value):
        if not hasattr(self, name):
            if name not in self._allowed:
                raise LookupError("Invalid setting : %s"%name)
        super().__setattr__(name, value)

    ## @brief This method do the job for SettingsHandler.load_module()
    #
    # @note The difference with SettingsHandler.load_module() is that it didn't check if some settings are missing
    # @throw LokkupError if an invalid settings is given
    # @param module : a loaded module
    def _load_module(self, module):
        errors = []
        fatal_errors = []
        conf_dict = {
            name: getattr(module, name)
            for name in dir(module) 
            if not name.startswith('__') and not isinstance(getattr(module, name), types.ModuleType)
        }
        for name, value in conf_dict.items():
            try:
                setattr(self, name, value)
            except LookupError:
                errors.append(name)
        if len(errors) > 0:
            err_msg = "Found invalid settings in %s : %s"%(module.__name__, errors)
            raise LookupError(err_msg)

    ## @brief If some settings are missings return their names
    # @return an array of string
    def _missings(self):
        return [ confname for confname in self._mandatory if not hasattr(self, confname) ]

    def _set_loaded(self, value):
        super().__setattr__('_loaded', bool(value))

Settings = SettingsHandler()

## @page lodel_settings Lodel SettingsHandler
#
# This page describe the way settings are handled in Lodel2.
#
# @section lodel_settings_files Lodel settings files
#
# - Lodel/settings.py defines the Lodel.settings package, the SettingsHandler class and the Lodel.settings.Settings instance
# - Lodel/settings_format.py defines the mandatory and allowed configurations keys lists
# - install/instance_settings.py is a model of the file that will be deployed in Lodel2 instances directories
#
# @section Using Lodel.settings.Settings SettingsHandler instance
#
# @subsection lodel_settings_without_loader Without loader
#
# Without any loader you can import Lodel.settings.Settings and acces its property with getattr (or . ) or with SettingsHandler.get() method.
# In the same way you can set a settings by standart affectation of a propery or with SettingsHandler.set() method.
#
# @subsection lodel_settings_loader With a loader in a lodel2 instance
#
# The loader will import Lodel.settings.Settings and then calls the SettingsHandler.load_module() method to load the content of the instance_settings.py file into the SettingsHandler instance
#
# @subsection lodel_settings_example Examples
#
# <pre>
# #!/usr/bin/python
# from Lodel.settings import Settings
# if Settings.debug:
#   print("DEBUG")
# # or
# if Settings.get('debug'):
#   print("DEBUG")
# Settings.debug = False
# # or
# Settings.set('debug', False)
# </pre>
# 
