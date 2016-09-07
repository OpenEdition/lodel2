# -*- coding: utf-8 -*-

from lodel.settings.validator import SettingValidator

CONFSPEC = {
    'lodel2.sessions':{
        'directory': ('/tmp/', SettingValidator('path')),
        'expiration': (900, SettingValidator('int')),
        'file_template': ('lodel2_%s.sess', SettingValidator('dummy')),
        'tokensize': (512, SettingValidator('int'))
    }
}
