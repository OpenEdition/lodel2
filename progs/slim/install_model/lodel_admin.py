#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
import os, os.path
import argparse

##@brief Dirty hack to avoid problems with simlink to lodel2 lib folder
#
#In instance folder we got a loader.py (the one we want to import here when
#writing "import loader". The problem is that lodel_admin.py is a simlink to
#LODEL2LIB_FOLDER/install/lodel_admin.py . In this folder there is the 
#generic loader.py template. And when writing "import loader" its 
#LODEL2LIB_FOLDER/install/loader.py that gets imported.
#
#In order to solve this problem the _simlink_hack() function delete the
#LODEL2LIB_FOLDER/install entry from sys.path
#@todo delete me
def _simlink_hack():
    sys.path[0] = os.getcwd() #In order to override default ./ path

##@brief Return true if we are in a monosite instance
#@todo find a better way to achieve this
def _monosite_test():
    return os.path.isdir('./conf.d')

## @brief Utility method to generate python code given an emfile and a
# translator
# @param model_file str : An em file
# @param translator str : a translator name
# @return python code as string
def generate_dyncode(model_file, translator):
    from lodel.editorial_model.model import EditorialModel
    from lodel.leapi import lefactory
    
    model = EditorialModel.load(translator, filename  = model_file)
    dyncode = lefactory.dyncode_from_em(model)
    return dyncode

## @brief Utility method to generate a python file representing leapi dyncode
# given an em file and the associated translator name
#
# @param model_file str : An em file
# @param translator str : a translator name
# @param output_filename str : the output file
def create_dyncode(model_file, translator, output_filename):
    from lodel import logger
    dyncode = generate_dyncode(model_file, translator)
    with open(output_filename, 'w+') as out_fd:
        out_fd.write(dyncode)
    out_fd.close()
    logger.info("Dynamic leapi code written in %s", output_filename)


## @brief Refresh dynamic leapi code from settings
#@todo make it compatible with multisite : create a "real" progs that takes
#conf path in args
def refresh_dyncode():
    #import loader
    from lodel.context import LodelContext
    LodelContext.init()
    from lodel.settings.settings import Settings as settings_loader

    CONFDIR = os.path.join(os.getcwd(), 'conf.d')
    settings_loader(CONFDIR)
    from lodel.settings import Settings
    # EditorialModel update/refresh
    
    # TODO

    # Dyncode refresh
    create_dyncode( Settings.editorialmodel.emfile,
                    Settings.editorialmodel.emtranslator,
                    Settings.editorialmodel.dyncode)


def init_all_dbs():
    import loader
    loader.start()
    import leapi_dyncode as dyncode
    from lodel.plugin.datasource_plugin import DatasourcePlugin
    from lodel.settings.utils import SettingsError
    from lodel.leapi.leobject import LeObject
    from lodel.plugin import Plugin
    from lodel import logger

    ds_cls = dict() # EmClass indexed by rw_datasource
    for cls in dyncode.dynclasses:
        ds = cls._datasource_name
        if ds not in ds_cls:
            ds_cls[ds] = [cls]
        else:
            ds_cls[ds].append(cls)
    
    for ds_name in ds_cls:
        mh = DatasourcePlugin.init_migration_handler(ds_name)
        #Retrieve plugin_name & ds_identifier for logging purpose
        plugin_name, ds_identifier = DatasourcePlugin.plugin_name(
            ds_name, False)
        try:
            mh.init_db(ds_cls[ds_name])
        except Exception as e:
            msg = "Migration failed for datasource %s(%s.%s) when running \
init_db method: %s"
            msg %= (ds_name, plugin_name, ds_identifier, e)
        logger.info("Database initialisation done for %s(%s.%s)" % (
            ds_name, plugin_name, ds_identifier))

def list_registered_hooks():
    import loader
    loader.start()
    from lodel.plugin.hooks import LodelHook
    hlist = LodelHook.hook_list()
    print("Registered hooks are : ")
    for name in sorted(hlist.keys()):
        print("\t- %s is registered by : " % name)
        for reg_hook in hlist[name]:
            hook, priority = reg_hook
            msg = "\t\t- {modname}.{funname} with priority : {priority}"
            msg = msg.format(
                modname = hook.__module__,
                funname = hook.__name__,
                priority = priority)
            print(msg)
        print("\n")

##@brief update plugin's discover cache
#@note impossible to give arguments from a Makefile...
#@todo write a __main__ to be able to run ./lodel_admin
def update_plugin_discover_cache(path_list = None):
    os.environ['LODEL2_NO_SETTINGS_LOAD'] = 'True'
    import loader
    from lodel.plugin.plugins import Plugin
    res = Plugin.discover()
    print("Plugin discover result in %s :\n" % res['path_list'])
    for pname, pinfos in res['plugins'].items():
        print("\t- %s %s -> %s" % (
            pname, pinfos['version'], pinfos['path']))

if __name__ == '__main__':
    _simlink_hack()
    from lodel import bootstrap
    #to deleted when we known wich action need what kind of MULTISITE API
    if not bootstrap._monosite_test():
        bootstrap.bootstrap('lodelsites')
    else:
        bootstrap.bootstrap()
    from lodel.context import LodelContext
    #from lodel.plugin.scripts import main_run
    LodelContext.expose_modules(globals(),
        {'lodel.plugin.scripts': ['main_run'],
         'lodel.plugin.core_scripts': 'core_scripts'})
    main_run()
