# -*- coding: utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.validator': ['SettingValidator']})

##@brief Mongodb datasource plugin confspec
#@ingroup plugin_mongodb_datasource
#
#Describe mongodb plugin configuration. Keys are :
CONFSPEC = {
    'lodel2.datasource.mongodb_datasource.*':{
        'read_only': (False, SettingValidator('bool')),
        'host': ('localhost', SettingValidator('host')),
        'port': (None, SettingValidator('string', none_is_valid = True)),
        'db_name':('lodel', SettingValidator('string')),
        'username': (None, SettingValidator('string')),
        'password': (None, SettingValidator('string'))
    }
}
