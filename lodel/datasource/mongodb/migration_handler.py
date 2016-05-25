# -*- coding: utf-8 -*-

from lodel.datasource.generic.migrationhandler import GenericMigrationHandler
from lodel.datasource.mongodb.datasource import MongoDbDataSource
import lodel.datasource.mongodb.utils as utils
from lodel.editorial_model.components import EmClass, EmField


class MigrationHandlerChangeError(Exception):
    pass


class MongoDbMigrationHandler(GenericMigrationHandler):
    pass