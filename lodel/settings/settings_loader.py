#-*- coding: utf-8 -*-

## @brief Merges and loads configuration files
class SettingsLoader(object):
    ## @brief Constructor
    # @param conf_path str : conf.d path
    def __init__(self,conf_path):
        pass
    
    ## @brief Lists and merge files in settings_loader.conf_path
    #
    # 
    # @return dict()
    # 
    def __merge(self) :
        pass
    
    ## @brief Returns option if exists default_value else and validates
    # @param section str : name of the section
    # @param keyname str
    # @param validator callable : takes one argument value and raises validation fail
    # @param default_value *
    # @param mandatory bool
    # @return the option
    def getoption(self,section,keyname,validator,default_value,mandatory=False):
        pass
    
    ## @brief Returns the section to be configured
    # @param section_prefix str
    # @param default_section str
    # @return the section name
    def getsection(self,section_prefix,default_section):
        pass
    
    ## @brief Returns the sections which have not been configured
    # @return list of missing options
    def getremains(self):
        pass