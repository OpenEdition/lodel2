#-*- coding:utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.utils.mlstring': ['MlString']})

## @package lodel.mlnamedobject Lodel2 description of objects module
#
# Display name and Description of a lodel2 object

## @brief Represents a multi-language object (dealing with its translations) 
class MlNamedObject(object):
    
    ##
    # @param display_name str|dict : displayed string to name the object (either a string or a dictionnary of the translated strings can be passed)
    # @param help_text str|dict : description text for this object (either a string or a dictionnary of the translated strings can be passed)
    def __init__(self, display_name=None, help_text=None):
        ## @brief The object's name which will be used in all the user interfaces
        self.display_name = None if display_name is None else MlString(display_name)
        ## @brief Description text for this object
        self.help_text = None if help_text is None else MlString(help_text)
