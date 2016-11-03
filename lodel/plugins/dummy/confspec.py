#-*- coding: utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.validator': ['SettingValidator']})

CONFSPEC = {
    'lodel2.section1': {
        'key1': (   None,
                    SettingValidator('dummy'))
    }
}
