from lodel.plugin import LodelHook

from .datasource import MongoDbDatasource as Datasource

@LodelHook('datasources_migration_init')
def mongodb_migration_handler_init():
    import plugins.mongodb_datasource.migration_handler as migration_handler

