# -*- coding: utf-8 -*-
## @package refreshdyn Python script designed to generate dynamic API
# @see leapi.lefactory

import sys
from EditorialModel.model import Model
from leapi.lefactory import LeFactory
from EditorialModel.backend.json_backend import EmBackendJson
from DataSource.MySQL.leapidatasource import LeDataSourceSQL
import acl.factory

if len(sys.argv) > 1:
    raise NotImplementedError("Not implemented (broken because of leapi dyn module name)")

OUTPUT = 'leapi/dyn.py' if len(sys.argv) == 1 else sys.argv[1]
EMJSON = 'EditorialModel/test/me.json' if len(sys.argv) < 3 else sys.argv[2]
LEAPI_MODNAME = 'leapi.dyn'

ACL_OUTPUT = 'acl/dyn.py'

em = Model(EmBackendJson(EMJSON))

fact = LeFactory(OUTPUT)
fact.create_pyfile(em, LeDataSourceSQL, {})
print(fact.generate_python(em, LeDataSourceSQL, {}))
fact = acl.factory.AclFactory(ACL_OUTPUT)
fact.create_pyfile(em, LEAPI_MODNAME)
print(fact.generate_python(em, LEAPI_MODNAME))


