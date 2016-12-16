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
    sys.path.append(LODEL2_LIB_ABS_PATH)

try:
    import lodel
except ImportError as e:
    print("Unable to load lodel module. exiting...")
    print(e)
    exit(1)

#Set context to MONOSITE
from lodel.context import LodelContext
LodelContext.init()

if 'LODEL2_NO_SETTINGS_LOAD' not in os.environ:
    #
    # Loading settings
    #
    LodelContext.expose_modules(globals(), {
        'lodel.settings.settings': [('Settings', 'settings')]})
    if not settings.started():
        settings('conf.d')
    LodelContext.expose_modules(globals(), {
        'lodel.settings': ['Settings']})
    
    #Starts hooks
    LodelContext.expose_modules(globals(), {
        'lodel.plugin': ['LodelHook'],
	'lodel.plugin.core_hooks': 'core_hooks',
	'lodel.plugin.core_scripts': 'core_scripts'})

def start():
    #Load plugins
    LodelContext.expose_modules(globals(), {
        'lodel.logger': 'logger',
        'lodel.plugin': ['Plugin']})
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
        runner = unittest.TextTestRunner(
            failfast = '-f' in sys.argv,
            verbosity = 2 if '-v' in sys.argv else 1)
        runner.run(suite)
        exit()

    lodel = LodelContext.get()
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
