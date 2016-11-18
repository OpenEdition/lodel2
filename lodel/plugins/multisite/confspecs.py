from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.validator': ['SettingValidator']})

#Define a minimal confspec used by multisite loader
LODEL2_CONFSPECS = {
    'lodel2': {
        'debug': (True, SettingValidator('bool'))
    },
    'lodel2.server': {
        'listen_address': ('', SettingValidator('dummy')),
        #'listen_address': ('', SettingValidator('ip')), #<-- not implemented
        'listen_port': ( 1337, SettingValidator('int')),
        'max_children': (40, SettingValidator('int')),
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
