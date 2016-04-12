#-*- coding: utf-8 -*-
import configparser
import os
import glob
import copy

from lodel.settings.utils import *

   
##@brief Merges and loads configuration files
class SettingsLoader(object):
    ##@brief Constructor
    # @param conf_path str : conf.d path
    def __init__(self,conf_path):
        self.__conf_path=conf_path
        self.__conf_sv=set()
        self.__conf=self.__merge()
    
    ##@brief Lists and merges files in settings_loader.conf_path
    #
    # 
    # @return dict()
    # 
    def __merge(self):
        conf = dict()
        dir_conf = os.open(self.__conf_path, os.O_RDONLY)
 
        l_dir = glob.glob(self.__conf_path+'/*.ini')  

        for f_ini in l_dir:  
            config = configparser.ConfigParser(default_section = 'lodel2')
            config.read(f_ini)
            for sect in config:
                if sect in conf:
                    for param in config[sect]:
                        if param not in conf[sect]: 
                            conf[sect][param] = config[sect][param]
                            if sect != 'DEFAULT': self.__conf_sv.add(sect + ':' + param)
                        else:
                            raise SettingsError("Key attribute already define : %s" % sect + ' '+param)                        
                else:
                    opts={}
                    for key in config[sect]:
                        opts[key] = config[sect].get(key)
                        if sect != 'DEFAULT': self.__conf_sv.add(sect + ':' + key)
                    conf.update({sect: opts})
        os.close(dir_conf)
        return conf
        
        
    
    ##@brief Returns option if exists default_value else and validates
    # @param section str : name of the section
    # @param keyname str
    # @param validator callable : takes one argument value and raises validation fail
    # @param default_value *
    # @param mandatory bool
    # @return the option
    def getoption(self,section,keyname,validator,default_value=None,mandatory=False):
        conf=copy.copy(self.__conf)
        sec=conf[section]
        if keyname in sec:
            optionstr=sec[keyname]
            option=validator(sec[keyname])
            self.__conf_sv.remove(section + ':' + keyname)
            return option
        elif mandatory:
             raise SettingsError("Default value mandatory for option %s" % keyname)
        else:
             return default_value
                              
    
    ##@brief Returns the section to be configured
    # @param section_prefix str
    # @param default_section str
    # @return the section as dict()
    def getsection(self,section_prefix,default_section=None):
        conf=copy.copy(self.__conf)
        if section_prefix in conf:
            return conf[section_prefix]
        elif default_section in conf: 
            return conf[default_section]
        return [];
    
    ##@brief Returns the sections which have not been configured
    # @return list of missing options
    def getremains(self):
        return list(self.__conf_sv)
        
