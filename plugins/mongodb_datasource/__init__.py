__loader__ = "main.py"
__confspec__ = "confspec.py"
__author__ = "Lodel2 dev team"
__fullname__ = "MongoDB plugin"


## @brief Activates the plugin
#
# @note It is possible there to add some specific actions (like checks, etc ...) for the plugin
#
# @return bool|str : True if all the checks are OK, an error message if not
def _activate():
    return True