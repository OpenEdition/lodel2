from lodel.settings.validator import SettingValidator

__plugin_name__ = "dummy"
__version__ = '0.0.1' #or __version__ = [0,0,1]
__loader__ = "main.py"
__confspec__ = "confspec.py"
__author__ = "Lodel2 dev team"
__fullname__ = "Dummy plugin"
__name__ = 'yweber.dummy'


##@brief This methods allow plugin writter to write some checks
#
#@return True if checks are OK else return a string with a reason
def _activate():
    import leapi_dyncode
    print("Testing dynamic objects : ")
    print("Object : ", leapi_dyncode.Object)
    print("Publication : ", leapi_dyncode.Publication)
    print("Publication fields : ", leapi_dyncode.Publication.fieldnames())
    return True
