#-*- coding:utf8 -*-

import pymysql
import os

sitename = 'em_editor'
lodel2_lib_path = '/home/yannweb/dev/lodel2/lodel2-git'

templates_base_dir = 'LODEL2_INSTANCE_TEMPLATES_BASE_DIR'

debug = False

em_file = 'em.pickle'
dynamic_code_file = 'dynleapi.py'

ds_package = 'picklediff'
datasource_options = {
    'filename': '/tmp/em_em.json',
}
