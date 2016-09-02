##@ingroup plugin_mongodb_datasource
class MongoDbDataSourceError(Exception):
    pass

##@ingroup plugin_mongodb_datasource
class MongoDbConsistencyError(MongoDbDataSourceError):
    pass

##@ingroup plugin_mongodb_datasource
class MigrationHandlerChangeError(Exception):
    pass


##@ingroup plugin_mongodb_datasource
class MigrationHandlerError(Exception):
    pass

