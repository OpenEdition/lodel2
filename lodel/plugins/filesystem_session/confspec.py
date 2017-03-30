# -*- coding: utf-8 -*-

## @package lodel.plugins.filesystem_session.confspec A module that defines the configuration options available for that plugin

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

## @brief Dictionary of the options and their corresponding validators
CONFSPEC = {
    'lodel2.sessions':{
        'directory': ('/tmp/', Validator('path')),
        'expiration': (900, Validator('int')),
        'file_template': ('lodel2_%s.sess', Validator('dummy'))
    }
}
