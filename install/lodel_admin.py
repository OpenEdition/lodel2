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
    import leapi_dyncode
    #TODO
    pass
