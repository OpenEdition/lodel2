#-*- coding:utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.utils.mlstring': ['MlString']})

## @package lodel.mlnamedobject Lodel2 description of objects module
#
# Display name and Description of a lodel2 object

##@brief Class allows dislpay name and help text for lodel2 objects and fields
class MlNamedObject(object):

    def __init__(self, display_name=None, help_text=None):
        self.display_name = None if display_name is None else MlString(display_name)
        self.help_text = None if help_text is None else MlString(help_text)
