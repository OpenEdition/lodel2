#-*- coding: utf-8 -*-

import sys
import os.path
import re
import socket
import inspect
import copy


## @package lodel.settings.validator Lodel2 settings validators/cast module
#
# Validator are registered in the SettingValidator class.
# @note to get a list of registered default validators just run
# <pre>$ python scripts/settings_validator.py</pre>

##@brief Exception class that should be raised when a validation fails
class SettingsValidationError(Exception):
    pass

##@brief Handles settings validators
#
# Class instance are callable objects that takes a value argument (the value to validate). It raises
# a SettingsValidationError if validation fails, else it returns a properly
# casted value.
class SettingValidator(object):
    
    _validators = dict()
    _description = dict()
    
    ##@brief Instanciate a validator
    def __init__(self, name, none_is_valid = False):
        if name is not None and name not in self._validators:
            raise NameError("No validator named '%s'" % name)
        self.__none_is_valid = none_is_valid
        self.__name = name

    ##@brief Call the validator
    # @param value *
    # @return properly casted value
    # @throw SettingsValidationError
    def __call__(self, value):
        if self.__name is None:
            return value
        if self.__none_is_valid and value is None:
            return None
        try:
            return self._validators[self.__name](value)
        except Exception as e:
            raise SettingsValidationError(e)
    
    ##@brief Register a new validator
    # @param name str : validator name
    # @param callback callable : the function that will validate a value
    # @param description str
    @classmethod
    def register_validator(cls, name, callback, description=None):
        if name in cls._validators:
            raise NameError("A validator named '%s' allready exists" % name)
        # Broken test for callable
        if not inspect.isfunction(callback) and not inspect.ismethod(callback) and not hasattr(callback, '__call__'):
            raise TypeError("Callable expected but got %s" % type(callback))
        cls._validators[name] = callback
        cls._description[name] = description
    
    ##@brief Get the validator list associated with description
    @classmethod
    def validators_list(cls):
        return copy.copy(cls._description)

    ##@brief Create and register a list validator
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
                elt = elt_validator(elt)
                if len(elt) > 0:
                    res.append(elt)
            return res
        description = "Convert value to an array" if description is None else description
        cls.register_validator(
                                validator_name,
                                list_validator,
                                description)
        return cls(validator_name)
 
    ##@brief Create and register a list validator which reads an array and returns a string
    # @param elt_validator callable : The validator that will be used for validate each elt value
    # @param validator_name str
    # @param description None | str
    # @param separator str : The element separator
    # @return A SettingValidator instance
    @classmethod
    def create_write_list_validator(cls, validator_name, elt_validator, description = None, separator = ','):
        def write_list_validator(value):
            res = ''
            errors = list()
            for elt in value:
                res += elt_validator(elt) + ','
            return res[:len(res)-1]
        description = "Convert value to a string" if description is None else description
        cls.register_validator(
                                validator_name,
                                write_list_validator,
                                description)
        return cls(validator_name)
    
    ##@brief Create and register a regular expression validator
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
    @classmethod
    def validators_list_str(cls):
        result = ''
        for name in sorted(cls._validators.keys()):
            result += "\t%016s" % name
            if name in cls._description and cls._description[name] is not None:
                result += ": %s" % cls._description[name]
            result += "\n"
        return result

##@brief Integer value validator callback
def int_val(value):
    return int(value)

##@brief Output file validator callback
# @return A file object (if filename is '-' return sys.stderr)
def file_err_output(value):
    if not isinstance(value, str):
        raise SettingsValidationError("A string was expected but got '%s' " % value)
    if value == '-':
        return None
    return value

##@brief Boolean value validator callback
def boolean_val(value):
    if isinstance(value, bool):
        return value
    if value.strip().lower() == 'true' or value.strip() == '1':
        value = True
    elif value.strip().lower() == 'false' or value.strip() == '0':
        value = False
    else:
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
        raise SettingsValidationError(
                "The value '%s' is not a valid loglevel" % value)
    return value.upper()

def path_val(value):
    if value is None or not os.path.exists(value):
        raise SettingsValidationError(
                "path '%s' doesn't exists" % value)
    return value

def none_val(value):
    if value is None:
        return None
    raise SettingsValidationError("This settings cannot be set in configuration file")

def str_val(value):
    try:
        return str(value)
    except Exception as e:
        raise SettingsValidationError("Not able to convert value to string : " + str(e))

def host_val(value):
    if value == 'localhost':
        return value
    ok = False
    try:
        socket.inet_aton(value)
        return value
    except (TypeError,OSError):
        pass
    try:
        socket.inet_pton(socket.AF_INET6, value)
        return value
    except (TypeError,OSError):
        pass
    try:
        socket.getaddrinfo(value, 80)
        return value
    except (TypeError,socket.gaierrror):
        msg = "The value '%s' is not a valid host"
        raise SettingsValidationError(msg % value)

def emfield_val(value):
    from lodel.plugin.hooks import LodelHook
    spl = value.split('.')
    if len(spl) != 2:
        msg = "Expected a value in the form CLASSNAME.FIELDNAME but got : %s"
        raise SettingsValidationError(msg % value)
    value = tuple(spl)
    #Late validation hook
    @LodelHook('lodel2_dyncode_bootstraped')
    def emfield_conf_check(hookname, caller, payload):
        from lodel import dyncode
        classnames = { cls.__name__.lower():cls for cls in dyncode.dynclasses}
        if value[0].lower() not in classnames:
            msg = "Following dynamic class do not exists in current EM : %s"
            raise SettingsValidationError(msg % value[0])
        ccls = classnames[value[0].lower()]
        if value[1].lower() not in ccls.fieldnames(True):
            msg = "Following field not found in class %s : %s"
            raise SettingsValidationError(msg % value)
    return value

def plugin_val(value):
    from lodel.plugin.hooks import LodelHook
    spl = value.split('.')
    if len(spl) != 2:
        msg = "Expected a value in the form PLUGIN.TYPE but got : %s"
        raise SettingsValidationError(msg % value)
    value = tuple(spl)
    #Late validation hook
    @LodelHook('lodel2_dyncode_bootstraped')
    def type_check(hookname, caller, payload):
        from lodel import plugin
        typesname = { cls.__name__.lower():cls for cls in plugin.PLUGINS_TYPE}
        if value[1].lower() not in typesname:
            msg = "Following plugin type do not exist in plugin list %s : %s"
            raise SettingsValidationError(msg % value)
        return value
    plug_type_val = plugin_val(value)
    return plug_type_val


#
#   Default validators registration
#

SettingValidator.register_validator(
    'plugin',
    plugin_val,
    'plugin validator')

SettingValidator.register_validator(
    'dummy',
    lambda value:value,
    'Validate anything')

SettingValidator.register_validator(
    'none',
    none_val,
    'Validate None')

SettingValidator.register_validator(
    'string',
    str_val,
    'Validate string values')

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

SettingValidator.register_validator(
    'path',
    path_val,
    'path validator')

SettingValidator.register_validator(
    'host',
    host_val,
    'host validator')

SettingValidator.register_validator(
    'emfield',
    emfield_val,
    'EmField name validator')

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
SettingValidator.create_write_list_validator(
    'write_list',
    SettingValidator('directory'),
    description = "Validator for an array of values which will be set in a string, separated by ','",
    separator = ',')
SettingValidator.create_re_validator(
    r'^https?://[^\./]+.[^\./]+/?.*$',
    'http_url',
    'Url validator')

#
#   Lodel 2 configuration specification
#

##@brief Append a piece of confspec
#@note orig is modified during the process
#@param orig dict : the confspec to update
#@param upd dict : the confspec to add
#@return new confspec
def confspec_append(orig, section, key, validator, default):
    if section not in orig:
        orig[section] = dict()
    if key not in orig[section]:
        orig[section][key] = (default, validator)
    return orig

##@brief Global specifications for lodel2 settings
LODEL2_CONF_SPECS = {
    'lodel2': {
        'debug': (  True,
                    SettingValidator('bool')),
        'sitename': (   'noname',
                        SettingValidator('strip')),
        'runtest': (    False,
                        SettingValidator('bool')),
    },
    'lodel2.logging.*' : {
        'level': (  'ERROR',
                    SettingValidator('loglevel')),
        'context': (    False,
                        SettingValidator('bool')),
        'filename': (   None,
                        SettingValidator('errfile', none_is_valid = True)),
        'backupcount': (    None,
                            SettingValidator('int', none_is_valid = True)),
        'maxbytes': (   None,
                        SettingValidator('int', none_is_valid = True)),
    },
    'lodel2.editorialmodel': {
        'emfile': ( 'em.pickle', SettingValidator('strip')),
        'emtranslator': ( 'picklefile', SettingValidator('strip')),
        'dyncode': ( 'leapi_dyncode.py', SettingValidator('strip')),
        'groups': ( '', SettingValidator('list')),
        'editormode': ( False, SettingValidator('bool')),
    },
    'lodel2.datasources.*': {
        'read_only': (False, SettingValidator('bool')),
        'identifier': ( None, SettingValidator('string')),
    },
    'lodel2.auth': {
        'login_classfield': ('user.login', SettingValidator('emfield')),
        'pass_classfield': ('user.password', SettingValidator('emfield')),
    },
}
