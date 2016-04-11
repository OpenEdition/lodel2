#-*- coding: utf-8 -*-
import configparser
import os
import glob
import copy

from lodel.settings.utils import *

## @brief Merges and loads configuration files
class SettingsLoader(object):
    ## @brief Constructor
    # @param conf_path str : conf.d path
    def __init__(self,conf_path):
        self.__conf_path=conf_path
        self.__conf_sv=set()
        self.__conf=self.__merge()
    
    ## @brief Lists and merges files in settings_loader.conf_path
    #
    # 
    # @return dict()
    # 
    def __merge(self):
        config = configparser.ConfigParser()
        conf = dict()
        dir_conf = os.open(self.__conf_path, os.O_RDONLY)
 
        l = glob.glob(self.__conf_path+'/*.ini')  
        for f in l:  
            config.read(f)
            for s in config:
                if s in conf:
                    for vs in config[s]:
                        if vs not in conf[s]: 
                            conf[s].update({vs:config[s][vs]})
                        else:
                             print(vs) #raise SettingsError("Key attribute already define : %s" % s + ' '+vs + ' ' + str(conf[s]))                        
                else:
                    opts={}
                    for key in config[s]:
                        opts[key] = config[s].get(key)
                    conf.update({s: opts})
                self.__conf_sv.add(str({s: opts}))
        os.close(dir_conf)
        return conf
        
        
    
    ## @brief Returns option if exists default_value else and validates
    # @param section str : name of the section
    # @param keyname str
    # @param validator callable : takes one argument value and raises validation fail
    # @param default_value *
    # @param mandatory bool
    # @return the option
    def getoption(self,section,keyname,validator,default_value=None,mandatory=False):
        if keyname in section:
            option=validator(section[keyname].split(','))
            self.conf_save.remove(section[keyname])
            return section[keyname]
        elif default_value is not None:
            return section[default_value]
        elif mandatory is True:
            raise SettingsError("Default value mandatory for option %s" % keyname)
        return None
                              
    
    ## @brief Returns the section to be configured
    # @param section_prefix str
    # @param default_section str
    # @return the section as dict()
    def getsection(self,section_prefix,default_section=None):
        conf=copy.copy(self.__conf)
        if section_prefix in conf:
            return conf[section_prefix]
        elif default_section in conf: 
            return conf[default_section]
        return None;
    
    ## @brief Returns the sections which have not been configured
    # @return list of missing options
    def getremains(self):
        return list(self.conf_save)
        