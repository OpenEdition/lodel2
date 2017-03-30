#-*- coding:utf-8 -*-

## @package lodel.plugins.dummy_datasource.main The main module of the plugin. 

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.plugin': ['LodelHook']})
from .datasource import DummyDatasource as Datasource

## @brief returns the migration handler of this plugin. 
# @retunr DummyMigrationHandler
def migration_handler_class():
    from .migration_handler import DummyMigrationHandler as migration_handler
    return migration_handler

