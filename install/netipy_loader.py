#-*- coding: utf-8 -*-

from loader import *
import sys
import code
from Lodel.user import UserContext

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise RuntimeError("Usage : %s client_ip")
    UserContext.init(sys.argv[1])
    print("""
        netipy interface of Lodel2 %s instance environment.

        Welcome %s.
        To authenticate use UserContext.authenticate(identifier, proof) function
""" % (Settings.sitename, UserContext.identity().username))
    code.interact(local=locals())
