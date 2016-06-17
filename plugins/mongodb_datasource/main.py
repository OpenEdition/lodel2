from lodel.plugin import LodelHook

from .datasource import MongoDbDatasource as Datasource

def migration_handler_class():
    from .migration_handler import MigrationHandler as migration_handler
    return migration_handler

