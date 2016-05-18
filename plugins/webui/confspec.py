#-*- coding: utf-8 -*-

from lodel.settings.validator import SettingValidator

CONFSPEC = {
    'lodel2.webui.sessions': {
        'directory': (  '/tmp/lodel2_session',
                        SettingValidator('path')),
        'expiration': ( 900,
                        SettingValidator('int')),
        'file_template': (  'lodel2_%s.sess',
                            SettingValidator('dummy')),
    }
}
