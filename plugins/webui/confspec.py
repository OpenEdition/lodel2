from lodel.settings.validator import SettingValidator

CONFSPEC = {
    'lodel2.webui': {
        'standalone': ( 'False',
                        SettingValidator('string')),
        'listen_address': ( '127.0.0.1',
                            SettingValidator('dummy')),
        'listen_port': (    '9090',
                            SettingValidator('int')),
        'virtualenv': (None,
                       SettingValidator('path', none_is_valid=True)),
        'uwsgicmd': ('/usr/bin/uwsgi_python3', SettingValidator('dummy')),
        'cookie_secret_key': ('ConfigureYourOwnCookieSecretKey', SettingValidator('dummy')),
        'cookie_session_id': ('lodel', SettingValidator('dummy'))
    },
    'lodel2.webui.sessions': {
        'directory': (  '/tmp',
                        SettingValidator('path')),
        'expiration': ( 900,
                        SettingValidator('int')),
        'file_template': (  'lodel2_%s.sess',
                            SettingValidator('dummy')),
    }
}
