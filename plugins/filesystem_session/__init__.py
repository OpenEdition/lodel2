from lodel.settings.validator import SettingValidator

__plugin_name__ = 'filesystem_session'
__version__ = [0,0,1]
__plugin_type__ = 'session_handler'
__loader__ = 'main.py'
__confspec__ = "confspec.py"
__author__ = "Lodel2 dev team"
__fullname__ = "FileSystem Session Store Plugin"


## @brief This methods allow plugin writter to write some checks
#
# @return True if checks are OK else returns a string with a reason
def _activate():
    return True
