# -*- coding: utf-8 -*-

from loader import *

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


