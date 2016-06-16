from lodel.settings.validator import SettingValidator

CONFSPEC = {
    'lodel2.webui': {
        'standalone': ( False,
                        SettingValidator('bool')),
        'listen_address': ( '127.0.0.1',
                            SettingValidator('dummy')),
        'listen_port': (    '9090',
                            SettingValidator('int')),
    },
    'lodel2.webui.sessions': {
        'directory': (  '/tmp/lodel2_session',
                        SettingValidator('path')),
        'expiration': ( 900,
                        SettingValidator('int')),
        'file_template': (  'lodel2_%s.sess',
                            SettingValidator('dummy')),
    }
}
