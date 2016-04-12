#-*- coding: utf-8 -*-

from lodel.settings.settings import Settings as SettingsHandler
settings = SettingsHandler.bootstrap()
if settings is not None:
    Settings = settings.confs
