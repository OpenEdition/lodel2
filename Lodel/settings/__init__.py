from Lodel.settings.defaults import *

DEBUG = True

if DEBUG:
    from Lodel.settings.dev import *
else:
    from Lodel.settings.production import *

try:
    from Lodel.settings.locale import *
except ImportError:
        pass
