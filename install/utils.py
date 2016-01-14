# -*- coding: utf-8 -*-

from loader import *
import warnings


def refreshdyn():
    import sys
    from EditorialModel.model import Model
    from leapi.lefactory import LeFactory
    from EditorialModel.backend.json_backend import EmBackendJson
    from DataSource.MySQL.leapidatasource import LeDataSourceSQL
    OUTPUT = Settings.dynamic_code_file
    EMJSON = Settings.em_file
    # Load editorial model
    em = Model(EmBackendJson(EMJSON))
    # Generate dynamic code
    fact = LeFactory(OUTPUT)
    # Create the python file
    fact.create_pyfile(em, LeDataSourceSQL, {})


def db_init():
    from EditorialModel.backend.json_backend import EmBackendJson
    from EditorialModel.model import Model
    mh = getattr(migrationhandler,Settings.mh_classname)()
    em = Model(EmBackendJson(Settings.em_file))
    em.migrate_handler(mh)


def em_graph(output_file = None, image_format = None):
    from EditorialModel.model import Model
    from EditorialModel.backend.json_backend import EmBackendJson
    from EditorialModel.backend.graphviz import EmBackendGraphviz
    import subprocess
    
    if image_format is None:
        if hasattr(Settings, 'em_graph_format'):
            image_format = Settings.em_graph_format
        else:
            image_format = 'png'
    if output_file is None:
        if hasattr(Settings, 'em_graph_output'):
            output_file = Settings.em_graph_output
        else:
            output_file = '/tmp/em_%s_graph.dot'
    image_format = image_format.lower()
    try:
        output_file = output_file%Settings.sitename
    except TypeError:
        warnings.warn("Bad filename for em_graph output. The filename should be in the form '/foo/bar/file_%s_name.png")
        pass

    dot_file = output_file+".dot"
    
    graphviz_bckend = EmBackendGraphviz(dot_file)
    edmod = Model(EmBackendJson(Settings.em_file))
    graphviz_bckend.save(edmod)
    dot_cmd = [
        "dot",
        "-T%s"%image_format,
        dot_file
    ]
    with open(output_file, "w+") as outfp:
        subprocess.check_call(dot_cmd, stdout=outfp)
    os.unlink(dot_file)
    print("Output image written in file : '%s'" % output_file)


def dir_init():
    import os

    # Templates
    print("Creating Base Templates ...")
    templates = {
        'base': {'file': 'base.html', 'content': '{% extends "templates/base.html" %}'},
        'base_backend': {'file': 'base_backend.html', 'content': '{% extends "templates/base_backend.html" %}'}
    }

    current_directory = os.path.dirname(os.path.abspath(__file__))
    templates_directory = os.path.join(current_directory,'templates')
    if not os.path.exists(templates_directory):
        os.makedirs(templates_directory)

    for _, template in templates.items():
        my_file_path = os.path.join(templates_directory, template['file'])
        if os.path.exists(my_file_path):
            os.unlink(my_file_path)
        with open(my_file_path, 'w') as my_file:
            my_file.write(template['content'])
        print("Created %s" % my_file_path)