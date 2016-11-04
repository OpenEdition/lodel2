# -*- coding: utf-8 -*-
import os
from lodel.context import LodelContext


def preload():
    # TODO Get this path dynamically
    LODEL_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    LODEL_INSTANCES_DIR = os.path.join(LODEL_BASE_DIR, 'lodelsites')
    LodelContext.init(LodelContext.MULTISITE)
    lodelsites_list = [sitename for sitename in os.listdir(LODEL_INSTANCES_DIR) if os.path.isdir(sitename)]

    for lodelsite_path in lodelsites_list:
        LodelContext.from_path(lodelsite_path)
        lodelcontext = LodelContext._contexts[lodelsite_path.split('/')[-1]]

        # Loading settings
        lodelcontext.expose_modules(globals(), {'lodel.settings.settings': [('Settings', 'settings')]})
        lodelcontext.expose_modules(globals(), {'lodel.settings': ['Settings']})

        # Loading hooks
        lodelcontext.expose_modules(globals(), {
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