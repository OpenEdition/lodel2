#!/usr/bin/python3
#-*- coding: utf-8 -*-


try:
    import lodel
except ImportError:
    print("Not installed in default PYTHON PATH, adding .. to sys.path")
    import sys
    sys.path.append('..')
    import lodel

print(lodel)

#Init LodelContext in MONOSITE mode to disable context handling
from lodel.context import LodelContext
LodelContext.init()

from lodel.settings.validator import SettingValidator
from lodel.settings.settings import Settings as settings_loader

##@brief Describe settings validation
CONFSPECS = {
    'lodel2': {
        'debug': (True, SettingValidator('bool')),
    },
    'lodel2.logging.*' : {
        'level': (  'ERROR',
                    SettingValidator('loglevel')),
        'context': (    False,
                        SettingValidator('bool')),
        'filename': (   "-",
                        SettingValidator('errfile', none_is_valid = False)),
        'backupcount': (    5,
                            SettingValidator('int', none_is_valid = False)),
        'maxbytes': (   1024*10,
                        SettingValidator('int', none_is_valid = False)),
    },
    'lodel2.editorialmodel': {
        'editormode': (True, SettingValidator('bool')),
    }
}

settings_loader('./conf.d', CONFSPECS)

from lodel.settings import Settings
from lodel.logger import logger

print(Settings.editorialmodel)
logger.error("Hello")


from lodel.editorial_model.model import EditorialModel
print("Started : ")
print(EditorialModel.list_datahandlers())
