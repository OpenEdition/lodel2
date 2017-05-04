from lodel.validator.validator import Validator
try:
    __plugin_name__ = "multisite"
    __version__ = '0.0.1' #or __version__ = [0,0,1]
    __loader__ = "main.py"
    __author__ = "Lodel2 dev team"
    __fullname__ = "Multisite plugin"
    __name__ = 'yweber.dummy'
    __plugin_type__ = 'extension'

    CONFSPEC = {
        'lodel2.server': {
            'port': (80,Validator('int')),
            'listen_addr': ('', Validator('string')),
        }
    }

except ContextError:
    pass

