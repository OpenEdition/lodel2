#-*- coding: utf-8 -*-

##@brief Lodel2 loader script
#
#@note If you want to avoid settings loading you can set the environment
#variable LODEL2_NO_SETTINGS_LOAD (see @ref install.lodel_admin.update_plugin_discover_cache()
#

import sys, os, os.path
import lodel.plugins.multisite.loader.preload as preload
import lodel.plugins.multisite.main as multisite
#
# Bootstraping
#
LODEL2_LIB_ABS_PATH = '/home/yannweb/dev/lodel2/lodel2-git'
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

#Set context
from lodel.context import LodelContext
LODEL2_CONTEXT_MODE = LodelContext.MULTISITE
LODEL2_SITES_PATH = '.'
LodelContext.init(LODEL2_CONTEXT_MODE)

if LODEL2_CONTEXT_MODE == LodelContext.MULTISITE:
    #Browse site's directory to set contextes
    l_dir = os.listdir(LODEL2_SITES_PATH)
    for entry in l_dir:
        if os.path.isdir(entry):
            LodelContext.from_path(entry)

def global_load():
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

if 'LODEL2_NO_SETTINGS_LOAD' not in os.environ:
    #
    # Loading settings
    #
    if LODEL2_CONTEXT_MODE == LodelContext.MULTISITE:
        #for ctx in LodelContext._contexts:
        #   LodelContext.set(ctx)
        #   global_load()
    else:
        global_load()

def load_loop(lodel):
    import leapi_dyncode as dyncode
    lodel.dyncode = dyncode
    LodelHook.call_hook('lodel2_dyncode_bootstraped', '__main__', None)
    #Run interative python
    import code
    print("""
     Running interactive python in Lodel2 %s instance environment
    """%Settings.sitename)
    code.interact(local=locals())
    
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

    if LODEL2_CONTEXT_MODE == LodelContext.MULTISITE:
        preload.preload()
    else:
        lodel = LodelContext.get()
        load_loop(lodel)

    multisite.main_loop()

