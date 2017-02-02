#-*- coding: utf-8 -*-

import sys

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.exceptions': ['LodelException', 'LodelExceptions',
        'LodelFatalError', 'FieldValidationError'],
    'lodel.validator.validator': ['Validator', 'ValidationError']})

## @package lodel.DhOptions.validator Lodel2 DhOptions validators/cast module
#
# Validator are registered in the DhOptionValidator class.
# @note to get a list of registered default validators just run
# <pre>$ python scripts/DhOptions_validator.py</pre>

##@brief Exception class that should be raised when a validation fails
class DhOptionValidationError(ValidationError):
    pass

##@brief Handles DhOptions validators
#
# Class instance are callable objects that takes a value argument (the value to validate). It raises
# a DhOptionsValidationError if validation fails, else it returns a properly
# casted value.
#@todo implement an IP validator and use it in multisite confspec
class DhOptionValidator(Validator):

    ##@brief Instanciate a validator
    #@param name str : validator name
    #@param none_is_valid bool : if True None will be validated
    #@param **kwargs : more arguement for the validator
    def __init__(self, name, none_is_valid = False, **kwargs):
        super().__init__(name, none_is_valid = False, **kwargs)

    ##@brief Call the validator
    # @param value *
    # @return properly casted value
    # @throw DhOptionsValidationError
    def __call__(self, value):
        super().__call__(value)

