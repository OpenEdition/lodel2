# -*- coding: utf-8 -*-
import os
import os.path
import warnings
LODEL2_INSTANCES_DIR = '.'
EXCLUDE_DIR = {'conf.d'}

try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext

LodelContext.init(LodelContext.MULTISITE)
LodelContext.set(None) #Loading context creation
#Multisite instance settings loading
CONFDIR = os.path.join(os.getcwd(), 'conf.d')
if not os.path.isdir(CONFDIR):
    warnings.warn('%s do not exists, default settings used' % CONFDIR)
LodelContext.expose_modules(globals(), {
    'lodel.settings.settings': [('Settings', 'settings')],
    'lodel.plugins.multisite.confspecs': 'multisite_confspecs'})
if not settings.started():
    settings('./conf.d', multisite_confspecs.LODEL2_CONFSPECS)

lodelsites_list = [ os.path.realpath(os.path.join(LODEL2_INSTANCES_DIR,sitename)) 
    for sitename in os.listdir(LODEL2_INSTANCES_DIR)
    if os.path.isdir(sitename) and sitename not in EXCLUDE_DIR]
for lodelsite_path in lodelsites_list:
    ctx_name = LodelContext.from_path(lodelsite_path)
    #Switch to new context
    LodelContext.set(ctx_name)
    os.chdir(lodelsite_path)
    # Loading settings
    LodelContext.expose_modules(globals(), {
        'lodel.settings.settings': [('Settings', 'settings')]})
    if not settings.started():
        settings('./conf.d')
    LodelContext.expose_modules(globals(), {'lodel.settings': ['Settings']})

    # Loading hooks & plugins
    LodelContext.expose_modules(globals(), {
        'lodel.plugin': ['LodelHook'],
        'lodel.plugin.core_hooks': 'core_hooks',
        'lodel.plugin.core_scripts': 'core_scripts'
    })

    #Load plugins
    LodelContext.expose_modules(globals(), {
        'lodel.logger': 'logger',
        'lodel.plugin': ['Plugin']})
    logger.debug("Loader.start() called")
    Plugin.load_all()
    #Import & expose dyncode
    LodelContext.expose_dyncode(globals())
    #Next hook triggers dyncode datasource instanciations
    LodelHook.call_hook('lodel2_plugins_loaded', '__main__', None)
    #Next hook triggers call of interface's main loop
    LodelHook.call_hook('lodel2_bootstraped', '__main__', None)
    #a dirty & quick attempt to fix context unwanted exite via
    #hooks
    for name in ( 'LodelHook', 'core_hooks', 'core_scripts',
            'Settings', 'settings', 'logger', 'Plugin'):
        del(globals()[name])
    #switch back to loader context
    LodelContext.set(None)

LodelContext.expose_modules(
    globals(), {'lodel.plugins.multisite.main': 'main'})
main.main_loop()

