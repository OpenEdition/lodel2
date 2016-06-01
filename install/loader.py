#-*- coding: utf-8 -*-

import sys, os
#
# Bootstraping
#
LODEL2_LIB_ABS_PATH = None
if LODEL2_LIB_ABS_PATH is not None:
    sys.path.append(os.path.dirname(LODEL2_LIB_ABS_PATH))

try:
    import lodel
except ImportError:
    print("Unable to load lodel module. exiting...")
    exit(1)


#
# Loading settings
#
from lodel.settings.settings import Settings as settings
settings('conf.d')
from lodel.settings import Settings


#Load plugins
from lodel.plugin import Plugin
Plugin.load_all()


from lodel.plugin import LodelHook

def start():
    #Importing dynamic code classes in lodel.leapi
    import leapi_dyncode
    import lodel.leapi
    for cls in leapi_dyncode.dynclasses:
        setattr(lodel.leapi, cls.__name__, cls)

    LodelHook.call_hook('lodel2_bootstraped', '__main__', None)


if __name__ == '__main__':
    start()
    LodelHook.call_hook('lodel2_loader_main', '__main__', None)
    #Run interative python
    import code
    print("""
     Running interactive python in Lodel2 %s instance environment

"""%Settings.sitename)
    code.interact(local=locals())
