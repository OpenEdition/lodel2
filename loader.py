#-*- coding: utf-8 -*-

import imp
import lodel.settings
from lodel.settings.settings import Settings
Settings.bootstrap(conf_file = 'settings_local.ini', conf_dir = 'globconf.d')
imp.reload(lodel.settings)
