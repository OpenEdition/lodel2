#-*- coding: utf-8 -*-

import sys
import os
import configparser
import copy
import warnings
import types  # for dynamic bindings
from collections import namedtuple

from lodel.context import LodelContext

LodelContext.expose_modules(globals(), {
    'lodel.logger': 'logger',
    'lodel.settings.utils': ['SettingsError', 'SettingsErrors'],
    'lodel.validator.validator': ['Validator', 'LODEL2_CONF_SPECS',
                                  'confspec_append'],
    'lodel.settings.settings_loader': ['SettingsLoader']})


##  @package lodel.settings.settings Lodel2 settings module
#
# Contains the class that handles the namedtuple tree of settings

## @brief A default python system lib path
PYTHON_SYS_LIB_PATH = '/usr/local/lib/python{major}.{minor}/'.format(

    major=sys.version_info.major,
    minor=sys.version_info.minor)


class MetaSettings(type):

    @property
    def s(self):
        self.singleton_assert(True)
        return self.instance.settings

## @brief Handles configuration load etc.
#
# To see howto bootstrap Settings and use it in lodel instance see
# @ref lodel.settings
#
# @par Basic instance usage
# For example if a file defines confs like :
# <pre>
# [super_section]
# super_conf = super_value
# </pre>
# You can access it with :
# <pre> settings_instance.confs.super_section.super_conf </pre>
#
# @par Init sequence
# The initialization sequence is a bit tricky. In fact, plugins adds allowed
# configuration sections/values, but the list of plugins to load are in... the
# settings.
# Here is the conceptual presentation of Settings class initialization stages :
#   -# Preloading (sets values like lodel2 library path or the plugins path)
#   -# Ask a @ref lodel.settings.setting_loader.SettingsLoader to load all
# configurations files
#   -# Fetch the list of plugins in the loaded settings
#   -# Merge plugins settings specification with the global lodel settings
# specs ( see @ref lodel.plugin )
#   -# Fetch all settings from the merged settings specs
#
# @par Init sequence in practical
# In practice those steps are done by calling a succession of private methods :
#   -# @ref Settings.__bootstrap() ( steps 1 to 3 )
#   -# @ref Settings.__merge_specs() ( step 4 )
#   -# @ref Settings.__populate_from_specs() (step 5)
#   -# And finally @ref Settings.__confs_to_namedtuple()
#
# @todo handles default sections for variable sections (sections ending with
# '.*')
# @todo delete the first stage, the lib path HAVE TO BE HARDCODED. In fact
# when we will run lodel in production the lodel2 lib will be in the python path
#@todo add log messages (now we can)


class Settings(object, metaclass=MetaSettings):

    ## @brief Stores the singleton instance
    instance = None

    ## @brief Instanciate the Settings singleton
    # @param conf_dir str : The configuration directory
    #@param custom_confspecs None | dict : if given overwrite default lodel2
    # confspecs
    def __init__(self, conf_dir, custom_confspecs=None):
        self.singleton_assert()  # check that it is the only instance
        Settings.instance = self
        #  @brief Configuration specification
        #
        # Initialized by Settings.__bootstrap() method
        self.__conf_specs = custom_confspecs
        #  @brief Stores the configurations in namedtuple tree
        self.__confs = None
        self.__conf_dir = conf_dir
        self.__started = False
        self.__bootstrap()

    ## @brief Get the named tuple representing configuration
    @property
    def settings(self):
        return self.__confs.lodel2

    ## @brief Delete the singleton instance
    @classmethod
    def stop(cls):
        del(cls.instance)
        cls.instance = None

    @classmethod
    def started(cls):
        return cls.instance is not None and cls.instance.__started

    ## @brief An utility method that raises if the singleton is not in a good
    # state
    #@param expect_instanciated bool : if True we expect that the class is
    # allready instanciated, else not
    # @throw RuntimeError
    @classmethod
    def singleton_assert(cls, expect_instanciated=False):
        if expect_instanciated:
            if not cls.started():
                raise RuntimeError("The Settings class is not started yet")
        else:
            if cls.started():
                raise RuntimeError("The Settings class is already started")

    ## @brief Saves a new configuration for section confname
    #@param confname is the name of the modified section
    #@param confvalue is a dict with variables to save
    #@param validator is a dict with adapted validator
    @classmethod
    def set(cls, confname, confvalue, validator):
        loader = SettingsLoader(cls.instance.__conf_dir)
        confkey = confname.rpartition('.')
        loader.setoption(confkey[0], confkey[2], confvalue, validator)

    # @brief This method handles Settings instance bootstraping
    def __bootstrap(self):
        LodelContext.expose_modules(globals(), {
            'lodel.plugin.plugins': ['Plugin', 'PluginError']})
        logger.debug("Settings bootstraping")
        if self.__conf_specs is None:
            lodel2_specs = LODEL2_CONF_SPECS
        else:
            lodel2_specs = self.__conf_specs
            self.__conf_specs = None
        loader = SettingsLoader(self.__conf_dir)
        plugin_list = []
        for ptype_name, ptype in Plugin.plugin_types().items():
            pls = ptype.plist_confspecs()
            lodel2_specs = confspec_append(lodel2_specs, **pls)
            cur_list = loader.getoption(
                pls['section'],
                pls['key'],
                pls['validator'],
                pls['default'])
            if cur_list is None:
                continue
            try:
                if isinstance(cur_list, str):
                    cur_list = [cur_list]
                plugin_list += cur_list
            except TypeError:
                plugin_list += [cur_list]

        # Remove invalid plugin names
        plugin_list = [plugin for plugin in plugin_list if len(plugin) > 0]

        # Checking confspecs
        for section in lodel2_specs:
            if section.lower() != section:
                raise SettingsError(
                    "Only lower case are allowed in section name (thank's ConfigParser...)")
            for kname in lodel2_specs[section]:
                if kname.lower() != kname:
                    raise SettingsError(
                        "Only lower case are allowed in section name (thank's ConfigParser...)")

        # Starting the Plugins class
        logger.debug("Starting lodel.plugin.Plugin class")
        Plugin.start(plugin_list)
        # Fetching conf specs from plugins
        specs = [lodel2_specs]
        errors = list()
        for plugin_name in plugin_list:
            try:
                specs.append(Plugin.get(plugin_name).confspecs)
            except PluginError as e:
                errors.append(SettingsError(msg=str(e)))
        if len(errors) > 0:  # Raise all plugins import errors
            raise SettingsErrors(errors)
        self.__conf_specs = self.__merge_specs(specs)
        self.__populate_from_specs(self.__conf_specs, loader)
        self.__started = True

    ## @brief Produce a configuration specification dict by merging all specifications
    #
    # Merges global lodel2 conf spec from @ref lodel.settings.validator.LODEL2_CONF_SPECS
    # and configuration specifications from loaded plugins
    # @param specs list : list of specifications dict
    # @return a specification dict
    def __merge_specs(self, specs):
        res = copy.copy(specs.pop())
        for spec in specs:
            for section in spec:
                if section.lower() != section:
                    raise SettingsError(
                        "Only lower case are allowed in section name (thank's ConfigParser...)")
                if section not in res:
                    res[section] = dict()
                for kname in spec[section]:
                    if kname.lower() != kname:
                        raise SettingsError(
                            "Only lower case are allowed in section name (thank's ConfigParser...)")
                    if kname in res[section]:
                        raise SettingsError("Duplicated key '%s' in section '%s'" %
                                            (kname, section))
                    res[section.lower()][kname] = copy.copy(spec[section][kname])
        return res

    ## @brief Populate the Settings instance with options values fetched with the loader from merged specs
    #
    # Populate the __confs attribute
    # @param specs dict : Settings specification dictionnary as returned by __merge_specs
    # @param loader SettingsLoader : A SettingsLoader instance
    def __populate_from_specs(self, specs, loader):
        self.__confs = dict()
        specs = copy.copy(specs)  # Avoid destroying original specs dict (may be useless)
        # Construct final specs dict replacing variable sections
        # by the actual existing sections
        variable_sections = [section for section in specs if section.endswith('.*')]
        for vsec in variable_sections:
            preffix = vsec[:-2]
            # WARNING : hardcoded default section
            for section in loader.getsection(preffix, 'default'):
                specs[section] = copy.copy(specs[vsec])
            del(specs[vsec])
        # Fetching values for sections
        for section in specs:
            for kname in specs[section]:
                validator = specs[section][kname][1]
                default = specs[section][kname][0]
                if section not in self.__confs:
                    self.__confs[section] = dict()
                self.__confs[section][kname] = loader.getoption(section, kname, validator, default)
        # Checking unfectched values
        loader.raise_errors()

        self.__confs_to_namedtuple()
        pass

    ## @brief Transform the __confs attribute into imbricated namedtuple
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
                section_name += sec_part + '.'
                if sec_part not in cur:
                    cur[sec_part] = dict()
                cur = cur[sec_part]
            section_name = section_name[:-1]
            for kname, kval in self.__confs[section_name].items():
                if kname in cur:
                    raise SettingsError("Duplicated key for '%s.%s'" % (section_name, kname))
                cur[kname] = kval

        path = [('root', section_tree)]
        visited = set()

        curname = 'root'
        nodename = 'Lodel2Settings'
        cur = section_tree
        while True:
            visited.add(nodename)
            left = [(kname, cur[kname])
                    for kname in cur
                    if nodename + '.' + kname.title() not in visited and isinstance(cur[kname], dict)
                    ]
            if len(left) == 0:
                name, leaf = path.pop()
                typename = nodename.replace('.', '')
                if len(path) == 0:
                    # END
                    self.__confs = self.__tree2namedtuple(leaf, typename)
                    break
                else:
                    path[-1][1][name] = self.__tree2namedtuple(leaf, typename)
                nodename = '.'.join(nodename.split('.')[:-1])
                cur = path[-1][1]
            else:
                curname, cur = left[0]
                path.append((curname, cur))
                nodename += '.' + curname.title()

    ## @brief Forge a named tuple given a conftree node
    # @param conftree dict : A conftree node
    # @param name str
    # @return a named tuple with fieldnames corresponding to conftree keys
    def __tree2namedtuple(self, conftree, name):
        ResNamedTuple = namedtuple(name, conftree.keys())
        return ResNamedTuple(**conftree)


class MetaSettingsRO(type):

    def __getattr__(self, name):
        return getattr(Settings.s, name)


## @brief A class that provide . notation read only access to configurations
class SettingsRO(object, metaclass=MetaSettingsRO):
    pass
