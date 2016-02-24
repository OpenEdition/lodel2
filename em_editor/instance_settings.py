#-*- coding:utf8 -*-

import pymysql
import os

sitename = 'em_editor'
lodel2_lib_path = '/home/yannweb/dev/lodel2/lodel2-git'

templates_base_dir = 'LODEL2_INSTANCE_TEMPLATES_BASE_DIR'

debug = False

em_file = 'em.json'
dynamic_code_file = 'dynleapi.py'

ds_package = 'MySQL'
mh_classname = 'MysqlMigrationHandler'
datasource = {
    'default': {
        'module': pymysql,
        'host': '127.0.0.1',
        'user': 'lodel',
        'passwd': 'bruno',
        'db': 'lodel2tests'
    }
}
