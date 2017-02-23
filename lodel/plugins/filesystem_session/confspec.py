# -*- coding: utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

CONFSPEC = {
    'lodel2.sessions':{
        'directory': ('/tmp/', Validator('path')),
        'expiration': (900, Validator('int')),
        'file_template': ('lodel2_%s.sess', Validator('dummy'))
    }
}
