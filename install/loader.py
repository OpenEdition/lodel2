import settings
import importlib
import sys
import os

sys.path.append(settings.lodel2_lib_path)

# Import dynamic code
if os.path.isfile(settings.dynamic_code):
    from dynleapi import *

# Import wanted datasource objects
for db_modname in ['leapidatasource', 'migrationhandler']:
    mod = importlib.import_module("DataSource.{pkg_name}.{mod_name}".format(
            pkg_name=settings.ds_package,
            mod_name=db_modname,
        )
    )
    # Expose the module in globals
    globals()[db_modname] = mod

if __name__ == '__main__':
    import code
    print("""
     Running interactive python in Lodel2 %s instance environment

"""%settings.name)
    code.interact(local=locals())
