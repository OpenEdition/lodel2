import settings as instance_settings
import importlib
import sys
import os

sys.path.append(instance_settings.lodel2_lib_path)

from Lodel.settings import Settings

# Update the settings
for name in [ name for name in dir(instance_settings) if not name.startswith('__') ]:
    Settings.set(name, getattr(instance_settings, name))

# Import dynamic code
if os.path.isfile(Settings.get('dynamic_code')):
    from dynleapi import *

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

"""%settings.name)
    code.interact(local=locals())
