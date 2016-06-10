from .utils import connect, get_connection_args

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
    default_connection_args = get_connection_args()
    connection_check = connect(
        default_connection_args['host'],
        default_connection_args['port'],
        default_connection_args['db_name'],
        default_connection_args['username'],
        default_connection_args['password'])
    if not connection_check:
        return False
    return True