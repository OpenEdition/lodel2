from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.settings.validator': ['SettingValidator']})

__plugin_name__ = "dummy"
__version__ = '0.0.1' #or __version__ = [0,0,1]
__loader__ = "main.py"
__confspec__ = "confspec.py"
__author__ = "Lodel2 dev team"
__fullname__ = "Dummy plugin"
__name__ = 'dummy'
__plugin_type__ = 'extension'


##@brief This methods allow plugin writter to write some checks
#
#@return True if checks are OK else return a string with a reason
def _activate():
    import leapi_dyncode
    print("Testing dynamic objects : ")
    print("Object : ", leapi_dyncode.Object)
    print("Collection : ", leapi_dyncode.Collection)
    print("Collection fields : ", leapi_dyncode.Collection.fieldnames())
    return True
