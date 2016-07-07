from lodel import logger

class AuthenticationError(Exception):
    pass

class AuthenticationFailure(Exception):
    
    def __init__(self, client):
        msg = "%s : authentication failure" % client
        logger.security(msg)
        super().__init__(msg)

