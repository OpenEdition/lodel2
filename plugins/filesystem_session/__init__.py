from lodel.settings.validator import SettingValidator

__loader__ = 'main.py'
__confspec__ = "confspec.py"
__author__ = "Lodel2 dev team"
__fullname__ = "FileSystem Session Store Plugin"


## @brief This methods allow plugin writter to write some checks
#
# @return True if checks are OK else returns a string with a reason
def _activate():
    return True