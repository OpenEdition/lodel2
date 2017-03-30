#-*- coding: utf-8 -*-

## @package lodel.plugins.dummy.confspec The module that defines the plugin's configuration options

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

## @brief Dictionary defining the plugin's configuration options and their validators
CONFSPEC = {
    'lodel2.section1': {
        'key1': (   None,
                    Validator('dummy'))
    }
}
