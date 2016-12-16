#-*- coding: utf-8 -*-
import configparser
import os
import glob
import copy

from lodel.context import LodelContext

LodelContext.expose_modules(globals(), {
    'lodel.logger': 'logger',
    'lodel.settings.utils': ['SettingsError', 'SettingsErrors'],
    'lodel.settings.validator': ['SettingsValidationError']})

##@brief Merges and loads configuration files
class SettingsLoader(object):
    
    ## To avoid the DEFAULT section whose values are found in all sections, we
    # have to give it an unsual name
    DEFAULT_SECTION = 'lodel2_default_passaway_tip'
    
    ## @brief Virtual filename when default value is used
    DEFAULT_FILENAME = 'default_value'

    ##@brief Constructor
    # @param conf_path str : conf.d path
    def __init__(self,conf_path):
        self.__conf_path=conf_path
        self.__conf_sv=dict()
        self.__conf=self.__merge()
        # Stores errors
        self.__errors_list = []
    
    ##@brief Lists and merges files in settings_loader.conf_path
    # @return dict()
    def __merge(self):
        conf = dict()
        l_dir = glob.glob(self.__conf_path+'/*.ini')
        logger.debug("SettingsLoader found those settings files : %s" % (
            ', '.join(l_dir)))

        for f_ini in l_dir:  
            config = configparser.ConfigParser(default_section = self.DEFAULT_SECTION ,interpolation=None)
            config.read(f_ini)
            for section in [ s for s in config if s != self.DEFAULT_SECTION ]:
                if section not in conf:
                    conf[section] = dict()
                for param in config[section]:
                    if param not in conf[section]: 
                        conf[section][param]=dict()
                        conf[section][param]['value'] = config[section][param]
                        conf[section][param]['file'] = f_ini
                        self.__conf_sv[section + ':' + param]=f_ini
                    else:
                        raise SettingsError("Error redeclaration of key %s in section %s. Found in %s and %s" % (
            section,
            param,
            f_ini,
            conf[section][param]['file']))
        return conf
    
    ##@brief Returns option if exists default_value else and validates
    # @param section str : name of the section
    # @param keyname str
    # @param validator callable : takes one argument value and raises validation fail
    # @param default_value *
    # @param mandatory bool
    # @return the option
    def getoption(self,section,keyname,validator,default_value=None,mandatory=False):
        conf=self.__conf
        if section not in conf:
            conf[section] = dict()

        sec = conf[section]
        result = None
        if keyname in sec:
            result = sec[keyname]['value']
            if result is not None:
                result = result.strip()
                if len(result) == 0:
                    result = None
            try:
                del self.__conf_sv[section + ':' + keyname]
            except KeyError: #allready fetched
                pass
        if result is None:
            if default_value is None and mandatory:
                msg = "Default value mandatory for option %s" % keyname
                expt = SettingsError(   msg = msg,
                                        key_id = section+'.'+keyname,
                                        filename = sec[keyname]['file'])
                self.__errors_list.append(expt)
                return
            else:
                sec[keyname]=dict()
                sec[keyname]['value'] = default_value
                sec[keyname]['file'] = SettingsLoader.DEFAULT_FILENAME
                result = default_value
                logger.debug("Using default value for configuration key %s:%s" % (
                    section, keyname))

        try:
            return validator(result)
        except Exception as e:
            # Generating nice exceptions
            if False and sec[keyname]['file'] == SettingsLoader.DEFAULT_FILENAME:
                expt = SettingsError(   msg = 'Mandatory settings not found',
                                        key_id = section+'.'+keyname)
                self.__errors_list.append(expt)
            else:
                expt = SettingsValidationError(
                                                "For %s.%s : %s" % 
                                                (section, keyname,e)
                )
                expt2 = SettingsError(  msg = str(expt),
                                        key_id = section+'.'+keyname,
                                        filename = sec[keyname]['file'])
                self.__errors_list.append(expt2)
            return

    ##@brief Sets option in a config section. Writes in the conf file
    # @param section str : name of the section
    # @param keyname str
    # @param value str
    # @param validator callable : takes one argument value and raises validation fail
    # @return the option
    def setoption(self,section,keyname,value,validator):
        f_conf=copy.copy(self.__conf[section][keyname]['file'])
        if f_conf == SettingsLoader.DEFAULT_FILENAME:
            f_conf = self.__conf_path + '/generated.ini'

        conf=self.__conf
        conf[section][keyname] = value
        config = configparser.ConfigParser()
        config.read(f_conf)
        if section not in config:
            config[section]={}
        config[section][keyname] = validator(value)
        
        with open(f_conf, 'w') as configfile:
            config.write(configfile)
            
    ##@brief Saves new partial configuration. Writes in the conf files corresponding
    # @param sections dict
    # @param validators dict of callable : takes one argument value and raises validation fail
    def saveconf(self, sections, validators):
        for sec in sections:
            for kname in sections[sec]:
                self.setoption(sec,kname,sections[sec][kname],validators[sec][kname])
    
    ##@brief Returns the section to be configured
    # @param section_prefix str
    # @param default_section str
    # @return the section as dict()
    def getsection(self,section_prefix,default_section=None):
        conf=copy.copy(self.__conf)
       
        sections=[]
        if section_prefix in conf:
            sections.append(section_prefix)
        for sect_names in conf:
            if sect_names in sections:
                pass
            elif sect_names.startswith(section_prefix + '.'):
                sections.append(sect_names)
        if sections == [] and default_section: 
             sections.append(section_prefix + '.' + default_section)
        elif sections == []:
            raise NameError("Not existing settings section : %s" % section_prefix)
            
        return sections
    
    ##@brief Returns invalid settings
    #
    # This method returns all the settings that was not fecthed by 
    # getsection() method. For the Settings object it allows to know
    # the list of invalids settings keys
    # @return a dict with SECTION_NAME+":"+KEY_NAME as key and the filename
    # where the settings was found as value
    def getremains(self):
        return self.__conf_sv
    
    ##@brief Raise a SettingsErrors exception if some confs remains
    #@note typically used at the end of Settings bootstrap
    def raise_errors(self):
        remains = self.getremains()
        err_l = self.__errors_list
        for key_id, filename in remains.items():
            err_l.append(SettingsError( msg = "Invalid configuration key",
                                        key_id = key_id,
                                        filename = filename))
        if len(err_l) > 0:
            raise SettingsErrors(err_l)
        else:
            return

