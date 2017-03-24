# @package lodel.auth.exceptions
# @brief Defines the specific exceptions used in the authentication process

from lodel.context import LodelContext

LodelContext.expose_modules(globals(), {
    'lodel.logger': 'logger',
    'lodel.plugin.hooks': ['LodelHook']})


## @brief Handles common errors with a Client
class ClientError(Exception):
    ## @brief The logger function to use to log the error message
    _loglvl = 'warning'
    ## @brief Error string
    _err_str = "Error"
    ## @brief the hook name to trigger with error
    _action = 'lodel2_ui_error'
    ## @brief the hook payload
    _payload = None

    ## @brief Constructor
    #
    # Log messages are built using the following format :
    # "<client infos> : <_err_str>[ : <msg>]"
    # @param client Client : object containing the client's data
    # @param msg str : message string to use
    def __init__(self, client, msg = ""):
        msg = self.build_message(client, msg)
        if self._loglvl is not None:
            logfun = getattr(logger, self._loglvl)
            logfun(msg)
        super().__init__(msg)
        if self._action is not None:
            LodelHook.call_hook(self._action, self, self._payload)

    ## @brief Builds an error message
    # @param client Client
    # @param msg str
    def build_message(self, client, msg):
        res = "%s : %s" % (client, self._err_str)
        if len(msg) > 0:
            res += " : %s" % msg
        return res


## @brief Handles authentication failure errors
class ClientAuthenticationFailure(ClientError):
    ## @brief Log Level
    _loglvl = 'security'
    ## @brief Error string
    _err_str = 'Authentication failure'
    ## @brief Hook to trigger
    _action = 'lodel2_ui_authentication_failure'


##@brief Handles permission denied errors
class ClientPermissionDenied(ClientError):
    ## @brief Log level
    _loglvl = 'security'
    ## @brief Error string
    _err_str = 'Permission denied'
    ## @brief Hook to trigger
    _action = 'lodel2_ui_permission_denied'
    

##@brief Handles common errors on authentication
class ClientAuthenticationError(ClientError):
    ## @brief Log level
    _loglvl = 'error'
    ## @brief Error string
    _err_str = 'Authentication error'
    ## @brief Hook to trigger
    _action = 'lodel2_ui_error'
