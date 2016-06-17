#-*- coding:utf-8 -*-

from lodel.plugin import LodelHook
from .datasource import DummyDatasource as Datasource

def migration_handler_class():
    from .migration_handler import DummyMigrationHandler as migration_handler
    return migration_handler

