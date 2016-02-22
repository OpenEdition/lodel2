#-*- coding: utf-8 -*-

from Lodel.user import authentication_method, identification_method, UserIdentity
from Lodel import logger

@authentication_method
def dummy_auth(identifier, proof):
    logger.info("User '%s' is trying to authenticate" % identifier)
    if identifier == proof:
        print("%s authenticated" % identifier)
        return UserIdentity(identifier, identifier, "User %s" % identifier, authenticated = True)
    else:
        logger.security("Authentication failed for user '%s'" % identifier)
        
    return False

@identification_method
def dummy_identify(client_infos):
    print("Trying to identify client with %s" % client_infos)
    if 'ip' in client_infos:
        ip = client_infos['ip']
        if ip in ['localhost', '127.0.0.1', 'local']:
            return UserIdentity(0, 'localuser', 'local user', identifier = True)
    return False

