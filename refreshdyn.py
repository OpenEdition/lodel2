# -*- coding: utf-8 -*-
## @package refreshdyn Python script designed to generate dynamic API
# @see leapi.lefactory

import sys
from EditorialModel.model import Model
from leapi.lefactory import LeFactory
from EditorialModel.backend.json_backend import EmBackendJson
from DataSource.MySQL.leapidatasource import LeDataSourceSQL

OUTPUT = 'leapi/dyn.py' if len(sys.argv) == 1 else sys.argv[1]
EMJSON = 'EditorialModel/test/me.json' if len(sys.argv) < 3 else sys.argv[2]

em = Model(EmBackendJson(EMJSON))

fact = LeFactory(OUTPUT)
fact.create_pyfile(em, LeDataSourceSQL, {})
print(fact.generate_python(em, LeDataSourceSQL, {}))


