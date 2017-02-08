##@brief 
#
#@par Notes on FS organisation
#
#The plan is as follow :
#
#The autotools deploiment chain or the debian package will create a var 
#folder dedicated for lodel2 ( for example /var/lodel2 ). This folder will
#contains folder named as the lodesites instances (lodelsites is a lodel site
#that handles lodel site as content). We will call this folder multisite
#folder or lodelsites folder.
#The multisite folder contains 2 settings folders :
#- lodelsites.conf.d : the lodelsites configuration
#- server.conf.d : the multisite process configuration
#- datas : a folder containing datas for each site handled by the lodelsites
#- .contexts : a folder containing context stuff for each site handlers by
#the lodelsites ( the lodel package symlink + dyncode.py)
#

from lodel.context import LodelContext, ContextError
try:
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

except ContextError:
    pass

