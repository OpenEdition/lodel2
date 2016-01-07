#-*- coding:utf8 -*-

import pymysql

sitename = 'LODEL2_INSTANCE_NAME'
lodel2_lib_path = 'LODEL2_LIB_ABS_PATH'

debug = False

em_file = 'em.json'
dynamic_code_file = 'dynleapi.py'

ds_package = 'MySQL'
mh_classname = 'MysqlMigrationHandler'
datasource = {
    'default': {
        'module': pymysql,
        'host': '127.0.0.1',
        'user': 'DBUSER',
        'passwd': 'DBPASSWORD',
        'db': 'DBNAME'
    }
}
