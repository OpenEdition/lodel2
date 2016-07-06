# -*- coding: utf-8 -*-

from lodel.settings.validator import SettingValidator

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
