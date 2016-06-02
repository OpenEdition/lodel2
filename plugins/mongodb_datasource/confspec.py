# -*- coding: utf-8 -*-

from lodel.settings.validator import SettingValidator

CONFSPEC = {
    'lodel2.datasource.mongodb_datasource.*':{
        'host': ('localhost', SettingValidator('host')),
        'port': (None, SettingValidator('string')),
        'db_name':('lodel', SettingValidator('string')),
        'username': (None, SettingValidator('string')),
        'password': (None, SettingValidator('string'))
    }
}