#-*- coding:utf8 -*-
## @package settings Configuration file

import os
import os.path

lodel2_lib_path = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.dirname(os.path.abspath(__file__))
debug = False
debug_sql = False

plugins = ['dummy', 'dummy_auth']

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

logging = {
    'stderr': {
        'level': 'INFO',
        'context': False,
    },
    'logfile': {
        'level': 'DEBUG',
        'filename': '/tmp/lodel2.log',
        'maxBytes': 1024 * 50, # rotate at 50MB
        'backupCount': 10, # keep at most 10 backup
        'context': True, # if false use a simpler format string
    }
}
