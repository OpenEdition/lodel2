from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin': ['LodelHook']})

from .datasource import MongoDbDatasource as Datasource

def migration_handler_class():
    from .migration_handler import MigrationHandler as migration_handler
    return migration_handler

