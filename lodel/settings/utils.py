#-*- coding: utf-8 -*-

## @package lodel.settings.utils Lodel 2 settings utility
#
# For now defines exception classes

##@brief Error class for settings errors
class SettingsError(Exception):
    
    ##@brief Instanciate a new SettingsError
    # @param msg str : Error message
    # @param key_id str : The key concerned by the error
    # @param filename str
    def __init__(self, msg = "Unknown error", key_id = None, filename = None):
        self.__msg = msg
        self.__key_id = key_id
        self.__filename = filename

    def __repr__(self): return str(self)

    def __str__(self):
        res = "Error "
        if self.__filename is not None:
            res += "in file '%s' " % self.__filename
        if self.__key_id is not None:
            res += "for key '%s'" % self.__key_id

        res += ": %s" % (self.__msg)
        return res

##@brief Designed to handles multiple SettingsError
class SettingsErrors(Exception):
    
    ##@brief Instanciate a SettingsErrors
    # @param exception list : list of SettingsError instance
    def __init__(self, exceptions):
        for expt in exceptions: 
            if not isinstance(expt, SettingsError):
                raise ValueError("The 'exceptions' argument has to be an array of <class SettingsError>, but a %s was found in the list" % type(expt))
        self.__exceptions = exceptions
        

    def __repr__(self): return str(self)

    ## @brief Return a string representation of a list of SettingError
    # This representation is the concatenation of all SettingError string representations
    def __str__(self):
        res = "Errors :\n"
        for expt in self.__exceptions:
            res += "\t%s\n" % str(expt)
        return res
