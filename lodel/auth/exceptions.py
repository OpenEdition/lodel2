from lodel import logger

def AuthenticationError(Exception):
    pass

def AuthenticationFailure(Exception):
    
    def __init__(self, client):
        msg = "%s : authentication failure" % client
        logger.security(msg)
        super().__init__(msg)

