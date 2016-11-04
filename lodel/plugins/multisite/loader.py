# -*- coding: utf-8 -*-
import os
from lodel.context import LodelContext


def preload():

    for lodelcontext in LodelContext._contexts:

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