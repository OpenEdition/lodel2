import os.path

try:
    from lodel.context import LodelContext
except ImportError:
    LODEL_BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lodel.context import LodelContext, ContextError

LodelContext.init(LodelContext.MULTISITE)

import lodel.buildconf #safe even outside contexts
from lodel.plugins.multisite.loader_utils import main, site_load, FAST_APP_EXPOSAL_CACHE

main() #multisite bootstraping

import code
print("""
    Running interactive python in Lodel2 multisite instance env.

    Note :  you are in LOAD_CTX environnment.
        use lodel.context.Lodelcontext.set(CONTEXT_NAME) to switch
""")
code.interact(local=locals())
