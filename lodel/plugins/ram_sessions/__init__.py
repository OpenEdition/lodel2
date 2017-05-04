from lodel.validator.validator Validator

__plugin_name__ = 'ram_sessions'
__version__ = [0,0,1]
__plugin_type__ = 'session_handler'
__loader__ = 'main.py'
__author__ = "Lodel2 dev team"
__fullname__ = "RAM Session Store Plugin"

CONFSPEC = {
    'lodel2.sessions':{
        'expiration': (900, Validator('int')),
        'tokensize': (512, Validator('int')),
    }
}
