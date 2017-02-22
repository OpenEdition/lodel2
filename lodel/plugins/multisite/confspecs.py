from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

#Define a minimal confspec used by multisite loader
LODEL2_CONFSPECS = {
    'lodel2': {
        'debug': (True, Validator('bool')),
    },
    'lodel2.lodelsites': {
        'name': (None,
            Validator('string', none_is_valid = False)), #Bad validator
        'lodelsites_emfile': (None,
            Validator('string', none_is_valid = False)), #Bad validator
        'lodelsites_emtranslator': ('picklefile',
            Validator('strip', none_is_valid = False)), #Bad validator
        'sites_emfile': (None,
            Validator('string', none_is_valid = False)), #Bad validator
        'sites_emtranslator': ('picklefile',
            Validator('string', none_is_valid = False)), #Bad validator
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
