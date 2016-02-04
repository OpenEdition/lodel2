import os
import importlib
from utils import dyn_code_filename
from Lodel.settings import Settings

# Import dynamic code
if Settings.acl_bypass:
    from dyncode.internal_api import *
else:
    from dyncode.acl_api import *

# Import wanted datasource objects
for db_modname in ['leapidatasource', 'migrationhandler']:
    mod = importlib.import_module("DataSource.{pkg_name}.{mod_name}".format(
            pkg_name=Settings.get('ds_package'),
            mod_name=db_modname,
        )
    )
    # Expose the module in globals
    globals()[db_modname] = mod

if __name__ == '__main__':
    import code
    print("""
     Running interactive python in Lodel2 %s instance environment

"""%Settings.sitename)
    code.interact(local=locals())
