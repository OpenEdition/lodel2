#-*- coding: utf-8 -*-

import sys
import os
import configparser
import copy
import warnings
from collections import namedtuple

from lodel.plugin.plugins import Plugins, PluginError
from lodel.settings.utils import SettingsError, SettingsErrors
from lodel.settings.validator import SettingValidator, LODEL2_CONF_SPECS
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

## @brief A default python system lib path
PYTHON_SYS_LIB_PATH = '/usr/local/lib/python{major}.{minor}/'.format(

                                                                        major = sys.version_info.major,
                                                                        minor = sys.version_info.minor)
## @brief Handles configuration load etc.
#
# @par Basic usage
# For example if a file defines confs like :
# <pre>
# [super_section]
# super_conf = super_value
# </pre>
# You can access it with :
# <pre> settings_instance.confs.super_section.super_conf </pre>
#
# @par Init sequence
# The initialization sequence is a bit tricky. In fact, plugins adds allowed configuration 
# sections/values, but the list of plugins to load in in... the settings.
# Here is the conceptual presentation of Settings class initialization stages :
#   -# Preloading (sets values like lodel2 library path or the plugins path)
#   -# Ask a @ref lodel.settings.setting_loader.SettingsLoader to load all configurations files
#   -# Fetch the list of plugins in the loaded settings
#   -# Merge plugins settings specification with the global lodel settings specs ( see @ref lodel.plugin )
#   -# Fetch all settings from the merged settings specs
#
# @par Init sequence in practical
# In practice those steps are done by calling a succession of private methods :
#   -# @ref Settings.__bootstrap() ( steps 1 to 3 )
#   -# @ref Settings.__merge_specs() ( step 4 )
#   -# @ref Settings.__populate_from_specs() (step 5)
#   -# And finally @ref Settings.__confs_to_namedtuple()
#
# @todo handles default sections for variable sections (sections ending with '.*')
class Settings(object):
    
    ## @brief global conf specsification (default_value + validator)
    _conf_preload = {
            'lib_path': (   PYTHON_SYS_LIB_PATH+'/lodel2/',
                            SettingValidator('directory')),
            'plugins_path': (   PYTHON_SYS_LIB_PATH+'lodel2/plugins/',
                                SettingValidator('directory_list')),
    }
    instance = None
    
    ## @brief Should be called only by the boostrap classmethod
    def __init__(self, conf_file = '/etc/lodel2/lodel2.conf', conf_dir = 'conf.d'):
        self.__confs = dict()
        self.__conf_dir = conf_dir
        self.__load_bootstrap_conf(conf_file)
        #   now we should have the self.__confs['lodel2']['plugins_paths']
        #   and self.__confs['lodel2']['lib_path'] set
        self.__bootstrap()
    
    ## @brief Stores as class attribute a Settings instance
    @classmethod
    def bootstrap(cls, conf_file = None, conf_dir = None):
        if cls.instance is None:
            if conf_file is None and conf_dir is None:
                warnings.warn("Lodel instance without settings !!!")
            else:
                cls.instance = cls(conf_file, conf_dir)
        return cls.instance

    ## @brief Configuration keys accessor
    # @return All confs organised into named tuples
    @property
    def confs(self):
        return copy.copy(self.__confs)

    ## @brief This method handlers Settings instance bootstraping
    def __bootstrap(self):
        lodel2_specs = LODEL2_CONF_SPECS
        plugins_opt_specs = lodel2_specs['lodel2']['plugins']

        # Init the settings loader
        loader = SettingsLoader(self.__conf_dir)
        # fetching list of plugins to load
        plugins_list = loader.getoption('lodel2', 'plugins', plugins_opt_specs[1], plugins_opt_specs[0], False)
        # Starting the Plugins class
        Plugins.bootstrap(self.__confs['lodel2']['plugins_path'])
        # Fetching conf specs from plugins
        specs = [lodel2_specs]
        errors = list()
        for plugin_name in plugins_list:
            try:
                specs.append(Plugins.get_confspec(plugin_name))
            except PluginError as e:
                errors.append(e)
        if len(errors) > 0: #Raise all plugins import errors
            raise SettingsErrors(errors)
        specs = self.__merge_specs(specs)
        self.__populate_from_specs(specs, loader)
    
    ## @brief Produce a configuration specification dict by merging all specifications
    #
    # Merges global lodel2 conf spec from @ref lodel.settings.validator.LODEL2_CONF_SPECS
    # and configuration specifications from loaded plugins
    # @param specs list : list of specifications dict
    # @return a specification dict
    def __merge_specs(self, specs):
        res = copy.copy(specs.pop())
        for spec in specs:
            for section in spec:
                if section not in res:
                    res[section] = dict()
                for kname in spec[section]:
                    if kname in res[section]:
                        raise SettingsError("Duplicated key '%s' in section '%s'" % (kname, section))
                    res[section][kname] = copy.copy(spec[section][kname])
        return res
    
    ## @brief Populate the Settings instance with options values fecthed with the loader from merged specs
    #
    # Populate the __confs attribute
    # @param specs dict : Settings specification dictionnary as returned by __merge_specs
    # @param loader SettingsLoader : A SettingsLoader instance
    def __populate_from_specs(self, specs, loader):
        specs = copy.copy(specs) #Avoid destroying original specs dict (may be useless)
        # Construct final specs dict replacing variable sections
        # by the actual existing sections
        variable_sections = [ section for section in specs if section.endswith('.*') ]
        for vsec in variable_sections:
            preffix = vsec[:-2]
            for section in loader.getsection(preffix, 'default'): #WARNING : hardcoded default section
                specs[section] = copy.copy(specs[vsec])
            del(specs[vsec])
        # Fetching valuds for sections
        for section in specs:
            for kname in specs[section]:
                validator = specs[section][kname][0]
                default = specs[section][kname][1]
                if section not in self.__confs:
                    self.__confs[section] = dict()
                self.__confs[section][kname] = loader.getoption(section, kname, validator, default)
        self.__confs_to_namedtuple()
        pass
    
    ## @brief Transform the __confs attribute into imbricated namedtuple
    #
    # For example an option named "foo" in a section named "hello.world" will
    # be acessible with self.__confs.hello.world.foo
    def __confs_to_namedtuple(self):
        res = None
        end = False

        splits = list()
        for section in self.__confs:
            splits.append(section.split('.'))
        max_len = max([len(spl) for spl in splits])
        # building a tree from sections splits
        section_tree = dict()
        for spl in splits:
            section_name = ""
            cur = section_tree
            for sec_part in spl:
                section_name += sec_part+'.'
                if sec_part not in cur:
                    cur[sec_part] = dict()
                cur = cur[sec_part]
            section_name = section_name[:-1]
            for kname, kval in self.__confs[section_name].items():
                if kname in cur:
                    raise SettingsError("Duplicated key for '%s.%s'" % (section_name, kname))
                cur[kname] = kval

        path = [ ('root', self.__confs) ]
        visited = list()
        
        curname = 'root'
        nodename = 'Root'
        cur = self.__confs
        while True:
            visited.append(cur)
            left = [    (kname, cur[kname])
                        for kname in cur
                        if cur[kname] not in visited and isinstance(cur[kname], dict)
                    ]
            if len(left) == 0:
                name, leaf = path.pop()
                typename = nodename.replace('.', '')
                if len(path) == 0:
                    # END
                    self.__confs = self.__tree2namedtuple(leaf,typename)
                    break
                else:
                    path[-1][1][name] = self.__tree2namedtuple(leaf,typename)
                nodename = '.'.join(nodename.split('.')[:-1])
            else:
                curname, cur = left[0]
                path.append( (curname, cur) )
                nodename += '.'+curname.title()
    
    ## @brief Forge a named tuple given a conftree node
    # @param conftree dict : A conftree node
    # @return a named tuple with fieldnames corresponding to conftree keys
    def __tree2namedtuple(self, conftree, name):
        ResNamedTuple = namedtuple(name, conftree.keys())
        return ResNamedTuple(**conftree)

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
        for keyname, (default, _) in self._conf_preload.items():
            res[keyname] = default

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

