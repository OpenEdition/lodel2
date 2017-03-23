##@brief
#
#Lodel2 multisite uwsgi plugin

from lodel.context import LodelContext, ContextError
try:
    LodelContext.expose_modules(globals(), {
        'lodel.validator.validator': ['Validator']})

    __plugin_type__ = 'ui' #Warning !!! It's a MULTISITE interface
    __plugin_name__ = 'multisite_web'
    __version__ = '0.0.1'
    __loader__ = 'main.py'
    #__plugin_deps__ = ['multisite']

    CONFSPEC = {
        'lodel2.server': {
                'listen_address': ('127.0.0.1', Validator('dummy')),
                #'listen_address': ('', Validator('ip')), #<-- not implemented
                'listen_port': ( 1337, Validator('int')),
                'uwsgi_workers': (8, Validator('int')),
                'uwsgicmd': ('/usr/bin/uwsgi', Validator('dummy')),
                'virtualenv': (None, Validator('path', none_is_valid = True)),
            },
        #A copy from webui confspec
        ##@todo automatic merging of webuig confspecs
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

except ContextError:
    #This case append when uwsgi call the run.py directly
    pass
