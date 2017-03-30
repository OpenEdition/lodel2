## @package lodel.plugins.dummy Basic plugin used as a template for developping new plugins

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.validator.validator': ['Validator']})

## @brief plugin's name (matching the package's name)
__plugin_name__ = "dummy"
## @brief plugin's version
__version__ = '0.0.1' #or __version__ = [0,0,1]
## @brief plugin's loader module
__loader__ = "main.py"
## @brief plugin's options' definition module
__confspec__ = "confspec.py"
## @brief plugin's author(s)
__author__ = "Lodel2 dev team"
## @brief plugin's full name
__fullname__ = "Dummy plugin"
__name__ = 'dummy'
## @brief plugin's category
__plugin_type__ = 'extension'


## @brief This methods allow plugin writter to write some checks
#
# @return bool : True if checks are OK else return a string with a reason
def _activate():
    import leapi_dyncode
    print("Testing dynamic objects : ")
    print("Object : ", leapi_dyncode.Object)
    print("Publication : ", leapi_dyncode.Publication)
    print("Publication fields : ", leapi_dyncode.Publication.fieldnames())
    return True
