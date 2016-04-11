#-*- coding: utf-8 -*-

import sys
import os.path
import re
import inspect
import copy

## @package lodel.settings.validator Lodel2 settings validators/cast module
#
# Validator are registered in the SettingValidator class.

class SettingsValidationError(Exception):
    pass

## @brief Handles settings validators
#
# Class instance are callable objects that takes a value argument (the value to validate). It raises
# a SettingsValidationError if validation fails, else it returns a properly
# casted value.
class SettingValidator(object):
    
    _validators = dict()
    _description = dict()
    
    ## @brief Instanciate a validator
    def __init__(self, name, none_is_valid = False):
        if name is not None and name not in self._validators:
            raise NameError("No validator named '%s'" % name)
        self.__name = name

    ## @brief Call the validator
    # @param value *
    # @return properly casted value
    # @throw SettingsValidationError
    def __call__(self, value):
        if self.__name is None:
            return value
        try:
            return self._validators[self.__name](value)
        except Exception as e:
            raise SettingsValidationError(e)
    
    ## @brief Register a new validator
    # @param name str : validator name
    # @param callback callable : the function that will validate a value
    @classmethod
    def register_validator(cls, name, callback, description=None):
        if name in cls._validators:
            raise NameError("A validator named '%s' allready exists" % name)
        # Broken test for callable
        if not inspect.isfunction(callback) and not inspect.ismethod(callback) and not hasattr(callback, '__call__'):
            raise TypeError("Callable expected but got %s" % type(callback))
        cls._validators[name] = callback
        cls._description[name] = description
    
    ## @brief Get the validator list associated with description
    @classmethod
    def validators_list(cls):
        return copy.copy(cls._description)

    ## @brief Create and register a list validator
    # @param elt_validator callable : The validator that will be used for validate each elt value
    # @param validator_name str
    # @param description None | str
    # @param separator str : The element separator
    # @return A SettingValidator instance
    @classmethod
    def create_list_validator(cls, validator_name, elt_validator, description = None, separator = ','):
        def list_validator(value):
            res = list()
            errors = list()
            for elt in value.split(separator):
                res.append(elt_validator(elt))
            return res
        description = "Convert value to an array" if description is None else description
        cls.register_validator(
                                validator_name,
                                list_validator,
                                description)
        return cls(validator_name)
                
    ## @brief Create and register a regular expression validator
    # @param pattern str : regex pattern
    # @param validator_name str : The validator name
    # @param description str : Validator description
    # @return a SettingValidator instance
    @classmethod
    def create_re_validator(cls, pattern, validator_name, description = None):
        def re_validator(value):
            if not re.match(pattern, value):
                raise SettingsValidationError("The value '%s' doesn't match the following pattern '%s'" % pattern)
            return value
        #registering the validator
        cls.register_validator(
                                validator_name,
                                re_validator,
                                ("Match value to '%s'" % pattern) if description is None else description)
        return cls(validator_name)

    
    ## @return a list of registered validators
    def validators_list_str(cls):
        result = ''
        for name in cls._validators:
            result += "\t%s" % name
            if name in self._description and self._description[name] is not None:
                result += "\t: %s" % self._description[name]
            result += "\n"
        return result

## @brief Integer value validator callback
def int_val(value):
    return int(value)

## @brief Output file validator callback
# @return A file object (if filename is '-' return sys.stderr)
def file_err_output(value):
    if not isinstance(value, str):
        raise SettingsValidationError("A string was expected but got '%s' " % value)
    if value == '-':
        return sys.stderr
    return value

## @brief Boolean value validator callback
def boolean_val(value):
    if not (value is True) and not (value is False):
        raise SettingsValidationError("A boolean was expected but got '%s' " % value)
    return bool(value)

def directory_val(value):
    res = SettingValidator('strip')(value)
    if not os.path.isdir(res):
        raise SettingsValidationError("Folowing path don't exists or is not a directory : '%s'"%res)
    return res

def loglevel_val(value):
    valids = ['DEBUG', 'INFO', 'SECURITY', 'ERROR', 'CRITICAL']
    if value.upper() not in valids:
        raise SettingsValidationError("The value '%s' is not a valid loglevel")

#
#   Default validators registration
#

SettingValidator.register_validator(
                                        'strip',
                                        str.strip,
                                        'String trim')

SettingValidator.register_validator(
                                        'int',
                                        int_val,
                                        'Integer value validator')

SettingValidator.register_validator(
                                        'bool',
                                        boolean_val,
                                        'Boolean value validator')

SettingValidator.register_validator(
                                        'errfile',
                                        file_err_output,
                                        'Error output file validator (return stderr if filename is "-")')

SettingValidator.register_validator(
                                        'directory',
                                        directory_val,
                                        'Directory path validator')

SettingValidator.register_validator(
                                        'loglevel',
                                        loglevel_val,
                                        'Loglevel validator')

SettingValidator.create_list_validator(
                                            'list',
                                            SettingValidator('strip'),
                                            description = "Simple list validator. Validate a list of values separated by ','",
                                            separator = ',')

SettingValidator.create_list_validator(
                                            'directory_list',
                                            SettingValidator('directory'),
                                            description = "Validator for a list of directory path separated with ','",
                                            separator = ',')

SettingValidator.create_re_validator(
                                        r'^https?://[^\./]+.[^\./]+/?.*$',
                                        'http_url',
                                        'Url validator')

#
#   Lodel 2 configuration specification
#

## @brief Global specifications for lodel2 settings
LODEL2_CONF_SPECS = {
    'lodel2': {
        'debug': (  True,
                    SettingValidator('bool')),
        'plugins': (    "",
                        SettingValidator('list')),
    },
    'lodel2.logging.*' : {
        'level': (  'ERROR',
                    SettingValidator('loglevel')),
        'context': (    False,
                        SettingValidator('bool')),
        'filename': (   None,
                        SettingValidator('errfile', none_is_valid = True)),
        'backupCount': (    None,
                            SettingValidator('int', none_is_valid = True)),
        'maxBytes': (   None,
                        SettingValidator('int', none_is_valid = True)),
    }
}
