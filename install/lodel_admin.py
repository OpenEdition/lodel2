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
    import leapi_dyncode as dyncode
    from lodel.settings.utils import SettingsError
    from lodel.leapi.leobject import LeObject
    from lodel.plugin import Plugin
    ds_cls = dict() # EmClass indexed by rw_datasource
    for cls in dyncode.dynclasses:
        ds = cls._datasource_name
        if ds not in ds_cls:
            ds_cls[ds] = [cls]
        else:
            ds_cls.append(cls)
    
    for ds_name in ds_cls:  
        # Fetching datasource plugin name and datasource connection 
        # identifier
        try:
            plugin_name, ds_indentifier = LeObject._get_ds_pugin_name(
                ds_name, False)
        except (NameError, ValueError, RuntimeError):
            raise SettingsError("Datasource configuration error")
        # Fetching datasource connection option
        con_conf=LeObject._get_ds_connection_conf(ds_identifier, plugin_name)
        # Fetching migration handler class from plugin
        plugin_module = Plugin.get(plugin_name).loader_module()
        mh_cls = plugin_module.migration_handler
        #Instanciate the migrationhandler and start db initialisation
        mh = mh_cls(**con_conf)
        mh.init_db(ds_cls[ds_name])
        pass
        
    #TODO : iter on datasource, fetch ds module and ds option
    # then instanciate corresponfing MH with given options
    pass
