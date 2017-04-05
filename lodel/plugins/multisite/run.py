import os.path

"""
try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext, ContextError

import lodel.buildconf #safe even outside contexts
"""

from lodel.plugins.multisite.loader_utils import main, FAST_APP_EXPOSAL_CACHE
from lodel.bootstrap import site_load
from lodel.context import LodelContext

lodelsites_name = main() #multisite bootstraping

#Switching back to lodelsites context in order to trigger hooks
LodelContext.set(lodelsites_name)
LodelContext.expose_modules(globals(), {
    'lodel.plugin.hooks': ['LodelHook']})
LodelHook.call_hook('lodel2_loader_main', '__main__', None)
LodelContext.set(None)
#If a hook is registered in lodelsites context for lodel2_loader_main
#this function never returns

import code
print("""
    Running interactive python in Lodel2 multisite instance env.

    Note :  you are in LOAD_CTX environnment.
        use lodel.context.Lodelcontext.set(CONTEXT_NAME) to switch
""")
code.interact(local=locals())
