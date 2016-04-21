#-*- coding: utf-8 -*-

from lodel.settings.validator import SettingValidator

CONFSPEC = {
    'lodel2.section1': {
        'key1': (   None,
                    SettingValidator('dummy'))
    }
}
