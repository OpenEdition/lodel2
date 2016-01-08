#-*- coding:utf8 -*-
## @package settings Configuration file

import pymysql

debug = False
debug_sql = False

datasource = {
    'default': {
        'module':pymysql,
        'host': None,
        'user': None,
        'passwd': None,
        'db': None,
    }
}

migration_options = {
    'dryrun': False,
    'foreign_keys': True,
    'drop_if_exists': False,
}

em_graph_format = 'png'
em_graph_output = '/tmp/em_%s_graph.png'
