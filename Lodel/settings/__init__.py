from defaults import *

DEBUG = True

if DEBUG:
    from dev import *
else:
    from production import *

try:
    from locale import *
except ImportError:
        pass
