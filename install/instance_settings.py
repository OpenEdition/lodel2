#-*- coding:utf8 -*-

import pymysql
import os

sitename = 'LODEL2_INSTANCE_NAME'
lodel2_lib_path = 'LODEL2_LIB_ABS_PATH'

templates_base_dir = 'LODEL2_INSTANCE_TEMPLATES_BASE_DIR'

debug = False

em_file = 'em.json'
dynamic_code_file = 'dynleapi.py'

ds_package = 'MySQL'
datasource_options = {
    'default': {
        'module': pymysql,
        'host': '127.0.0.1',
        'user': 'DBUSER',
        'passwd': 'DBPASSWORD',
        'db': 'DBNAME'
    }
}

""" # example
ds_package = 'jsondiff'
datasource_options = { 'json_file': 'output.json' }
"""
