# -*- coding: utf-8 -*-
import os
import os.path
LODEL2_INSTANCES_DIR = '.'

try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext

lodelsites_list = [sitename for sitename in os.listdir(LODEL_INSTANCES_DIR) if os.path.isdir(sitename)]
for lodelsite_path in lodelsites_list:
    ctx_name = LodelContext.from_path(lodelsite_path)
    #Switch to new context
    LodelContext.set(ctx_name)
    os.cwd(lodelsite_path)
    # Loading settings
    LodelContext.expose_modules(globals(), {'lodel.settings.settings': [('Settings', 'settings')]})
    if not settings.started():
        settings('conf.d')
    LodelContext.expose_modules(globals(), {'lodel.settings': ['Settings']})

    # Loading hooks & plugins
    LodelContext.expose_modules(globals(), {
        'lodel.plugin': ['LodelHook'],
        'lodel.plugin.core_hooks': 'core_hooks',
        'lodel.plugin.core_scripts': 'core_scripts'
    })

    #Load plugins
    lodelcontext.expose_modules(globals(), {
        'lodel.logger': 'logger',
        'lodel.plugin': ['Plugin']})
    logger.debug("Loader.start() called")
    Plugin.load_all()
    LodelHook.call_hook('lodel2_bootstraped', '__main__', None)
    #switch back to loader context
    LodelContext.set(None)

import lodel.plugins.multisite.main as main
main.main_loop()

