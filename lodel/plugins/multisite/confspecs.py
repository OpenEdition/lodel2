from lodel.validator.validator import Validator

#Define a minimal confspec used by multisite loader
LODEL2_CONFSPECS = {
    'lodel2': {
        'debug': (True, Validator('bool'))
    },
    'lodel2.server': {
        'listen_address': ('127.0.0.1', Validator('dummy')),
        #'listen_address': ('', Validator('ip')), #<-- not implemented
        'listen_port': ( 1337, Validator('int')),
        'uwsgi_workers': (8, Validator('int')),
        'uwsgicmd': ('/usr/bin/uwsgi', Validator('dummy')),
        'virtualenv': (None, Validator('path', none_is_valid = True)),
    },
    'lodel2.logging.*' : {
        'level': (  'ERROR',
                    Validator('loglevel')),
        'context': (    False,
                        Validator('bool')),
        'filename': (   None,
                        Validator('errfile', none_is_valid = True)),
        'backupcount': (    10,
                            Validator('int', none_is_valid = False)),
        'maxbytes': (   1024*10,
                        Validator('int', none_is_valid = False)),
    },
    'lodel2.datasources.*': {
        'read_only': (False, Validator('bool')),
        'identifier': ( None, Validator('string')),
    }
}
