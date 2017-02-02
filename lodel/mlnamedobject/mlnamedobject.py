#-*- coding:utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.utils.mlstring': ['MlString'],
    'lodel.logger': 'logger',
    'lodel.settings': ['Settings'],
    'lodel.settings.utils': ['SettingsError']})

class MlNamedObject(object):
    
    def __init__(self, display_name, help_text):
        self.display_name = MlString(display_name)
        self.help_text = MlString(help_text)
        
