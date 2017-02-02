#-*- coding:utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.utils.mlstring': ['MlString'],
    'lodel.logger': 'logger',
    'lodel.settings': ['Settings'],
    'lodel.settings.utils': ['SettingsError']})

class MlNamedObject(object):
    
    def __init__(self, display_name = None, help_text = None):
        self.display_name = None if display_name is None else MlString(display_name)
        self.help_text = None if help_text is None else MlString(help_text)
        
