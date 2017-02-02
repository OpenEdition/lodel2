#-*- coding: utf-8 -*-

import sys
import os.path
import re
import socket
import inspect
import copy

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.exceptions': ['LodelException', 'LodelExceptions',
        'LodelFatalError', 'FieldValidationError'],
    'lodel.validator.validator': ['Validator', 'ValidationError']})

## @package lodel.settings.validator Lodel2 settings validators/cast module
#
# Validator are registered in the SettingValidator class.
# @note to get a list of registered default validators just run
# <pre>$ python scripts/settings_validator.py</pre>

##@brief Exception class that should be raised when a validation fails
class SettingValidationError(ValidationError):
    pass

##@brief Handles settings validators
#
# Class instance are callable objects that takes a value argument (the value to validate). It raises
# a SettingsValidationError if validation fails, else it returns a properly
# casted value.
#@todo implement an IP validator and use it in multisite confspec
class SettingValidator(Validator):

    ##@brief Instanciate a validator
    #@param name str : validator name
    #@param none_is_valid bool : if True None will be validated
    #@param **kwargs : more arguement for the validator
    def __init__(self, name, none_is_valid = False, **kwargs):
        super().__init__(name, none_is_valid = False, **kwargs)

    ##@brief Call the validator
    # @param value *
    # @return properly casted value
    # @throw SettingsValidationError
    def __call__(self, value):
        super().__call__(value)

##@brief Validator for Editorial model component
#
# Designed to validate a conf that indicate a class.field in an EM
#@todo modified the hardcoded dyncode import (it's a warning)
def emfield_val(value):
    LodelContext.expose_modules(globals(), {
        'lodel.plugin.hooks': ['LodelHook']})
    spl = value.split('.')
    if len(spl) != 2:
        msg = "Expected a value in the form CLASSNAME.FIELDNAME but got : %s"
        raise SettingsValidationError(msg % value)
    value = tuple(spl)
    #Late validation hook
    @LodelHook('lodel2_dyncode_bootstraped')
    def emfield_conf_check(hookname, caller, payload):
        import leapi_dyncode as dyncode # <-- dirty & quick
        classnames = { cls.__name__.lower():cls for cls in dyncode.dynclasses}
        if value[0].lower() not in classnames:
            msg = "Following dynamic class do not exists in current EM : %s"
            raise SettingsValidationError(msg % value[0])
        ccls = classnames[value[0].lower()]
        if value[1].lower() not in ccls.fieldnames(True):
            msg = "Following field not found in class %s : %s"
            raise SettingsValidationError(msg % value)
    return value

##@brief Validator for plugin name & optionnaly type
#
#Able to check that the value is a plugin and if it is of a specific type
def plugin_validator(value, ptype = None):
    LodelContext.expose_modules(globals(), {
        'lodel.plugin.hooks': ['LodelHook']})
    value = copy.copy(value)
    @LodelHook('lodel2_dyncode_bootstraped')
    def plugin_type_checker(hookname, caller, payload):
        LodelContext.expose_modules(globals(), {
            'lodel.plugin.plugins': ['Plugin'],
            'lodel.plugin.exceptions': ['PluginError']})
        if value is None:
            return
        try:
            plugin = Plugin.get(value)
        except PluginError:
            msg = "No plugin named %s found"
            msg %= value
            raise SettingsValidationError(msg)
        if plugin._type_conf_name.lower() != ptype.lower():
            msg = "A plugin of type '%s' was expected but found a plugin \
named  '%s' that is a '%s' plugin"
            msg %= (ptype, value, plugin._type_conf_name)
            raise SettingsValidationError(msg)
    return value



SettingValidator.register_validator(
    'plugin',
    plugin_validator,
    'plugin name & type validator')

SettingValidator.register_validator(
    'emfield',
    emfield_val,
    'EmField name validator')

#
#   Lodel 2 configuration specification
#

##@brief Append a piece of confspec
#@note orig is modified during the process
#@param orig dict : the confspec to update
#@param section str : section name
#@param key str
#@param validator SettingValidator : the validator to use to check this configuration key's value
#@param default
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
        'filename': (   "-",
                        SettingValidator('errfile', none_is_valid = False)),
        'backupcount': (    5,
                            SettingValidator('int', none_is_valid = False)),
        'maxbytes': (   1024*10,
                        SettingValidator('int', none_is_valid = False)),
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
