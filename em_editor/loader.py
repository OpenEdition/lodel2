import instance_settings
import importlib
import sys
import os

sys.path.append(instance_settings.lodel2_lib_path)

from Lodel.settings import Settings

# Settings initialisation
Settings.load_module(instance_settings)
globals()['Settings'] = Settings

from Lodel import logger # logger import and initialisation

from plugins import * #Load activated plugins

# Import dynamic code
if os.path.isfile(Settings.dynamic_code_file):
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

"""%Settings.sitename)
    code.interact(local=locals())
