#-*- coding: utf-8 -*-

## @brief Error class for settings errors
class SettingsError(Exception):
    
    ## @brief Instanciate a new SettingsError
    # @param msg str : Error message
    # @param key_id str : The key concerned by the error
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
        
