from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.validator': ['SettingValidator']})

__plugin_name__ = 'ram_sessions'
__version__ = [0,0,1]
__plugin_type__ = 'session_handler'
__loader__ = 'main.py'
__author__ = "Lodel2 dev team"
__fullname__ = "RAM Session Store Plugin"

CONFSPEC = {
    'lodel2.sessions':{
        'expiration': (900, SettingValidator('int')),
        'tokensize': (512, SettingValidator('int')),
    }
}
