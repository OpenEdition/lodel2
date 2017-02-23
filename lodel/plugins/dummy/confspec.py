#-*- coding: utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

CONFSPEC = {
    'lodel2.section1': {
        'key1': (   None,
                    Validator('dummy'))
    }
}
