# -*- coding: utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

## @brief Mongodb datasource plugin confspec
# @ingroup plugin_mongodb_datasource
#
# Describes mongodb plugin configuration and the corresponding validators
CONFSPEC = {
    'lodel2.datasource.mongodb_datasource.*':{
        'read_only': (False, Validator('bool')),
        'host': ('localhost', Validator('host')),
        'port': (None, Validator('string', none_is_valid = True)),
        'db_name':('lodel', Validator('string')),
        'username': (None, Validator('string')),
        'password': (None, Validator('string'))
    }
}
