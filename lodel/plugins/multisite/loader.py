# -*- coding: utf-8 -*-
import os
import os.path

try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext

def preload():
    # TODO Get this path dynamically but should be ./ everytime (we run
    #the loader from the good folder)
    LODEL_INSTANCE_DIR = './'
    LodelContext.init(LodelContext.MULTISITE)
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
        #switch back to loader context
        LodelContext.set(None)
