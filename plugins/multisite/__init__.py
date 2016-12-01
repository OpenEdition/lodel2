from lodel.settings.validator import SettingValidator

__plugin_name__ = "multisite"
__version__ = '0.0.1'
__loader__ = "main.py"
__confspec__ = "confspec.py"
__author__ = "Lodel2 dev team"
__fullname__ = "Plugin that allow a lodel2 instance to have lodel2 instance\
as data"
__name__ = 'core.multisite'
__plugin_type__ = 'extension'


##@brief This methods allow plugin writter to write some checks
#@return True if checks are OK else return a string with a reason
def _activate():
    return True
