from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.validator': ['SettingValidator']})

CONFSPEC = {
    'lodel2.webui': {
        'standalone': ( 'False',
                        SettingValidator('string')),
        'listen_address': ( '127.0.0.1',
                            SettingValidator('dummy')),
        'listen_port': (    '9090',
                            SettingValidator('int')),
        'static_url': (     'http://127.0.0.1/static/',
                            SettingValidator('regex', pattern =  r'^https?://[^/].*$')),
        'virtualenv': (None,
                       SettingValidator('path', none_is_valid=True)),
        'uwsgicmd': ('/usr/bin/uwsgi', SettingValidator('dummy')),
        'cookie_secret_key': ('ConfigureYourOwnCookieSecretKey', SettingValidator('dummy')),
        'cookie_session_id': ('lodel', SettingValidator('dummy')),
        'uwsgi_workers': (2, SettingValidator('int'))
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
