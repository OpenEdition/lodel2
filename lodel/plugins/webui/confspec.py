from lodel.validator.validator import Validator

CONFSPEC = {
    'lodel2.webui': {
        'standalone': ( 'False',
                        Validator('string')),
        'listen_address': ( '127.0.0.1',
                            Validator('dummy')),
        'listen_port': (    '9090',
                            Validator('int')),
        'static_url': (     'http://127.0.0.1/static/',
                            Validator('regex', pattern =  r'^https?://[^/].*$')),
        'virtualenv': (None,
                       Validator('path', none_is_valid=True)),
        'uwsgicmd': ('/usr/bin/uwsgi', Validator('dummy')),
        'cookie_secret_key': ('ConfigureYourOwnCookieSecretKey', Validator('dummy')),
        'cookie_session_id': ('lodel', Validator('dummy')),
        'uwsgi_workers': (2, Validator('int'))
    },
    'lodel2.webui.sessions': {
        'directory': (  '/tmp',
                        Validator('path')),
        'expiration': ( 900,
                        Validator('int')),
        'file_template': (  'lodel2_%s.sess',
                            Validator('dummy')),
    }
}
