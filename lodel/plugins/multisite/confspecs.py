from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.validator': ['SettingValidator']})

#Define a minimal confspec used by multisite loader
LODEL2_CONFSPECS = {
    'lodel2': {
        'debug': (True, SettingValidator('bool')),
    },
    'lodel2.lodelsites': {
        'name': (None,
            SettingValidator('string', none_is_valid = False)), #Bad validator
        'lodelsites_emfile': (None,
            SettingValidator('string', none_is_valid = False)), #Bad validator
        'lodelsites_emtranslator': ('picklefile',
            SettingValidator('strip', none_is_valid = False)), #Bad validator
        'sites_emfile': (None,
            SettingValidator('string', none_is_valid = False)), #Bad validator
        'site_emtranslator': ('picklefile',
            SettingValidator('string', none_is_valid = False)), #Bad validator
    },
    'lodel2.server': {
        'listen_address': ('127.0.0.1', SettingValidator('dummy')),
        #'listen_address': ('', SettingValidator('ip')), #<-- not implemented
        'listen_port': ( 1337, SettingValidator('int')),
        'uwsgi_workers': (8, SettingValidator('int')),
        'uwsgicmd': ('/usr/bin/uwsgi', SettingValidator('dummy')),
        'virtualenv': (None, SettingValidator('path', none_is_valid = True)),
    },
    'lodel2.logging.*' : {
        'level': (  'ERROR',
                    SettingValidator('loglevel')),
        'context': (    False,
                        SettingValidator('bool')),
        'filename': (   None,
                        SettingValidator('errfile', none_is_valid = True)),
        'backupcount': (    10,
                            SettingValidator('int', none_is_valid = False)),
        'maxbytes': (   1024*10,
                        SettingValidator('int', none_is_valid = False)),
    },
    'lodel2.datasources.*': {
        'read_only': (False, SettingValidator('bool')),
        'identifier': ( None, SettingValidator('string')),
    }
}
