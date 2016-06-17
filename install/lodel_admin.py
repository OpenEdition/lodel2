#-*- coding: utf-8 -*-

import sys
import os, os.path
import loader

from lodel.settings import Settings
from lodel import logger

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
    dyncode = generate_dyncode(model_file, translator)
    with open(output_filename, 'w+') as out_fd:
        out_fd.write(dyncode)
    out_fd.close()
    logger.info("Dynamic leapi code written in %s", output_filename)


## @brief Refresh dynamic leapi code from settings
def refresh_dyncode():
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
        # Fetching datasource plugin name and datasource connection 
        # identifier
        try:
            plugin_name, ds_identifier = LeObject._get_ds_plugin_name(
                ds_name, False)
        except (NameError, ValueError, RuntimeError):
            raise SettingsError("Datasource configuration error")
        # Fetching datasource connection option
        con_conf=LeObject._get_ds_connection_conf(ds_identifier, plugin_name)
        # Fetching migration handler class from plugin
        plugin_module = Plugin.get(plugin_name).loader_module()
        try:
            mh_cls = plugin_module.migration_handler_class()
        except NameError as e:
            raise RuntimeError("Malformed plugin '%s'. Missing \
migration_handler_class() function in loader file" % ds_name)
        #Instanciate the migrationhandler and start db initialisation
        try:
            mh = mh_cls(**con_conf)
        except Exception as e:
            msg = "Migration failed for datasource %s(%s.%s) at migration \
handler instanciation : %s"
            msg %= (ds_name, plugin_name, ds_identifier, e)
            raise RuntimeError(msg)
        try:
            mh.init_db(ds_cls[ds_name])
        except Exception as e:
            msg = "Migration failed for datasource %s(%s.%s) when running \
init_db method: %s"
            msg %= (ds_name, plugin_name, ds_identifier, e)
        logger.info("Database initialisation done for %s(%s.%s)" % (
            ds_name, plugin_name, ds_identifier))
        
