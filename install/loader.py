#-*- coding: utf-8 -*-

##@brief Lodel2 loader script
#
#@note If you want to avoid settings loading you can set the environment
#variable LODEL2_NO_SETTINGS_LOAD (see @ref install.lodel_admin.update_plugin_discover_cache()
#

import sys, os, os.path
#
# Bootstraping
#
LODEL2_LIB_ABS_PATH = None
if LODEL2_LIB_ABS_PATH is not None:
    if not os.path.isdir(LODEL2_LIB_ABS_PATH):
        print("FATAL ERROR : the LODEL2_LIB_ABS_PATH variable in loader.py is \
not correct : '%s'" % LODEL2_LIB_ABS_PATH, file=sys.stderr)
    sys.path.append(os.path.dirname(LODEL2_LIB_ABS_PATH))

try:
    import lodel
except ImportError as e:
    print("Unable to load lodel module. exiting...")
    print(e)
    exit(1)

if 'LODEL2_NO_SETTINGS_LOAD' not in os.environ:
    #
    # Loading settings
    #
    from lodel.settings.settings import Settings as settings
    if not settings.started():
        settings('conf.d')
    from lodel.settings import Settings

    #Starts hooks
    from lodel.plugin import LodelHook
    from lodel.plugin import core_hooks

def start():
    #Load plugins
    from lodel import logger
    from lodel.plugin import Plugin
    logger.debug("Loader.start() called")
    Plugin.load_all()
    LodelHook.call_hook('lodel2_bootstraped', '__main__', None)


if __name__ == '__main__':

    start()
    if Settings.runtest:
        import unittest
        import tests
        loader = unittest.TestLoader()
        test_dir = os.path.join(LODEL2_LIB_ABS_PATH, 'tests')
        suite = loader.discover(test_dir)
        print("DEBUG  : failfast  = ", '-f' in sys.argv, sys.argv)
        runner = unittest.TextTestRunner(
            failfast = '-f' in sys.argv,
            verbosity = 2 if '-v' in sys.argv else 1)
        runner.run(suite)
        exit()

    import lodel
    import leapi_dyncode as dyncode
    lodel.dyncode = dyncode
    LodelHook.call_hook('lodel2_dyncode_bootstraped', '__main__', None)
    LodelHook.call_hook('lodel2_loader_main', '__main__', None)

    #Run interative python
    import code
    print("""
     Running interactive python in Lodel2 %s instance environment

"""%Settings.sitename)
    code.interact(local=locals())
