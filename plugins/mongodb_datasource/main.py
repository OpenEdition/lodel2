from lodel.plugin import LodelHook

@LodelHook('mongodb_mh_init')
def mongodb_migration_handler_init():
    import plugins.mongodb_datasource.migration_handler as migration_handler

@LodelHook('mongodb_ds_init')
def mongodb_datasource_init():
    import plugins.mongodb_datasource.datasource as datasource