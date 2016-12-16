# -*- coding: utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.validator': ['SettingValidator']})

CONFSPEC = {
    'lodel2.sessions':{
        'directory': ('/tmp/', SettingValidator('path')),
        'expiration': (900, SettingValidator('int')),
        'file_template': ('lodel2_%s.sess', SettingValidator('dummy'))
    }
}
