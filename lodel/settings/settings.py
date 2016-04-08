#-*- coding: utf-8 -*-

import sys
import os
import configparser

from lodel.plugins import Plugins
from lodel.settings.utils import SettingsError, SettingsErrors
from lodel.settings.validator import SettingValidator
from lodel.settings.settings_loader import SettingsLoader

## @package lodel.settings Lodel2 settings package
#
# Contains all module that help handling settings

## @package lodel.settings.settings Lodel2 settings module
#
# Handles configuration load/parse/check.
#
# @subsection Configuration load process
#
# The configuration load process is not trivial. In fact loaded plugins are able to add their own options.
# But the list of plugins to load and the plugins options are in the same file, the instance configuration file.
#
# @subsection Configuration specification
#
# Configuration specification is divided in 2 parts :
# - default values
# - value validation/cast (see @ref Lodel.settings.validator.ConfValidator )
# 

PYTHON_SYS_LIB_PATH = '/usr/local/lib/python{major}.{minor}/'.format(

                                                                        major = sys.version_info.major,
                                                                        minor = sys.version_info.minor)
## @brief Handles configuration load etc.
class Settings(object):
    
    ## @brief global conf specsification (default_value + validator)
    _conf_preload = {
            'lib_path': (   PYTHON_SYS_LIB_PATH+'/lodel2/',
                            SettingValidator('directory')),
            'plugins_path': (   PYTHON_SYS_LIB_PATH+'lodel2/plugins/',
                                SettingValidator('directory_list')),
    }
    
    def __init__(self, conf_file = '/etc/lodel2/lodel2.conf', conf_dir = 'conf.d'):
        self.__confs = dict()
        
        self.__load_bootstrap_conf(conf_file)
        # now we should have the self.__confs['lodel2']['plugins_paths'] and
        # self.__confs['lodel2']['lib_path'] set
        self.__bootstrap()
    
    ## @brief This method handlers Settings instance bootstraping
    def __bootstrap(self):
        #loader = SettingsLoader(self.__conf_dir)

        # Starting the Plugins class
        Plugins.bootstrap(self.__confs['lodel2']['plugins_path'])
        specs = Plugins.get_confspec('dummy')
        print("Got specs : %s " % specs)
        
        # then fetch options values from conf specs
    
    ## @brief Load base global configurations keys
    #
    # Base configurations keys are :
    # - lodel2 lib path
    # - lodel2 plugins path
    #
    # @note return nothing but set the __confs attribute
    # @see Settings._conf_preload
    def __load_bootstrap_conf(self, conf_file):
        config = configparser.ConfigParser()
        config.read(conf_file)
        sections = config.sections()
        if len(sections) != 1 or sections[0].lower() != 'lodel2':
            raise SettingsError("Global conf error, expected lodel2 section not found")
        
        #Load default values in result
        res = dict()
        for keyname, (keyvalue, validator) in self._conf_preload.items():
            res[keyname] = keyvalue

        confs = config[sections[0]]
        errors = []
        for name in confs:
            if name not in res:
                errors.append(  SettingsError(
                                    "Unknow field",
                                    "lodel2.%s" % name,
                                    conf_file))
            try:
                res[name] = self._conf_preload[name][1](confs[name])
            except Exception as e:
                errors.append(SettingsError(str(e), name, conf_file))
        if len(errors) > 0:
            raise SettingsErrors(errors)
        
        self.__confs['lodel2'] = res

