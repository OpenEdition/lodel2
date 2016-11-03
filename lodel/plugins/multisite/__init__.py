from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.validator': ['SettingValidator']})

__plugin_name__ = "multisite"
__version__ = '0.0.1' #or __version__ = [0,0,1]
__loader__ = "main.py"
__author__ = "Lodel2 dev team"
__fullname__ = "Multisite plugin"
__name__ = 'yweber.dummy'
__plugin_type__ = 'extension'

CONFSPEC = {
    'lodel2.server': {
        'port': (80,SettingValidator('int')),
        'listen_addr': ('', SettingValidator('string')),
    }
}
