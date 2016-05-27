#-*- coding: utf-8 -*-

import sys
import os, os.path

sys.path.append(os.path.dirname(os.getcwd()+'/..'))
from lodel.settings.settings import Settings as settings
settings('globconf.d')
from lodel.settings import Settings

def generate_dyncode(model_file, translator):
    from lodel.editorial_model.model import EditorialModel
    from lodel.leapi import lefactory

    model = EditorialModel.load(translator, filename  = model_file)
    dyncode = lefactory.dyncode_from_em(model)
    return dyncode

def refresh_dyncode(model_file, translator, output_filename):
    dyncode = generate_dyncode(model_file, translator)
    with open(output_filename, 'w+') as out_fd:
        out_fd.write(dyncode)
    out_fd.close()

