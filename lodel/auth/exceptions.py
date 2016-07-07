from lodel import logger

##@brief Handles common errors on authentication
class AuthenticationError(Exception):
    pass


##@brief Handles authentication error with possible security issue
#
#@note Handle the creation of a security log message containing client info
class AuthenticationSecurityError(AuthenticationError):
    def __init__(self, client):
        msg = "%s : authentication error" % client
        logger.security(msg)
        super().__init__(msg)


##@brief Handles authentication failure
#
#@note Handle the creation of a security log message containing client info
class AuthenticationFailure(Exception):
    
    def __init__(self, client):
        msg = "%s : authentication failure" % client
        logger.security(msg)
        super().__init__(msg)
