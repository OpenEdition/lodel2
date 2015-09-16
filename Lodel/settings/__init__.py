import os
from Lodel.settings.defaults import *

DEBUG = True

if DEBUG:
    from Lodel.settings.dev import *
else:
    from Lodel.settings.production import *

if 'LODEL_MIGRATION_HANDLER_TESTS' in os.environ:
    from Lodel.settings.migrations import *

try:
    from Lodel.settings.locale import *
except ImportError:
        pass
