#-*- coding: utf-8 -*-

#
# This file should be imported in every tests files
#

from lodel.settings.settings import Settings
Settings.bootstrap(conf_file = 'settings.ini', conf_dir = 'globconf.d')
