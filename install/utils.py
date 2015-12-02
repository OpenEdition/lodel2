# -*- coding: utf-8 -*-

import settings
from settings import *
from loader import *

def refreshdyn():
    import sys
    from EditorialModel.model import Model
    from leapi.lefactory import LeFactory
    from EditorialModel.backend.json_backend import EmBackendJson
    from DataSource.MySQL.leapidatasource import LeDataSourceSQL
    OUTPUT = dynamic_code
    EMJSON = emfile
    # Load editorial model
    em = Model(EmBackendJson(EMJSON))
    # Generate dynamic code
    fact = LeFactory(OUTPUT)
    # Create the python file
    fact.create_pyfile(em, LeDataSourceSQL, {})

def db_init():
    from EditorialModel.backend.json_backend import EmBackendJson
    from EditorialModel.model import Model
    mh = getattr(migrationhandler,settings.mh_classname)(**(settings.datasource['default']))
    em = Model(EmBackendJson(settings.emfile))
    em.migrate_handler(mh)


