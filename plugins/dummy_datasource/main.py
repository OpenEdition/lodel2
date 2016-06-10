#-*- coding:utf-8 -*-

from lodel.plugin import LodelHook
from .datasource import DummyDatasource as Datasource

@LodelHook('datasources_migration_init')
def dummy_migration_handler_init():
    from .migration_handler import DummyMigrationHandler as migration_handler

