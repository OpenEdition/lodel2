#-*- coding: utf-8 -*-

import Lodel.settings_format
from Lodel.settings import Settings

Lodel.settings_format.ALLOWED.append('acl_settings')
Settings._refresh_format()
Settings.acl_settings = { 'super': 42, 'foo': None }

