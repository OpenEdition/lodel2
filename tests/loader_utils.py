#-*- coding: utf-8 -*-

#
# This file should be imported in every tests files
#

from lodel.settings.settings import Settings

if not Settings.started():
    Settings('tests/tests_conf.d')
