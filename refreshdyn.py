# -*- coding: utf-8 -*-

from EditorialModel.model import Model
from leapi.lefactory import LeFactory
from EditorialModel.backend.json_backend import EmBackendJson
from leapi.datasources.ledatasourcesql import LeDataSourceSQL

OUTPUT = 'leapi/dyn.py'

em = Model(EmBackendJson('EditorialModel/test/me.json'))

fact = LeFactory('leapi/dyn.py')
fact.create_pyfile(em, LeDataSourceSQL, {})
print(fact.generate_python(em, LeDataSourceSQL, {}))


