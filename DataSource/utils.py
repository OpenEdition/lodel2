#-*- coding:utf-8 -*-

import importlib
from Lodel.settings import Settings

def get_datasource_cls():
    module = importlib.import_module("DataSource.{pkg_name}.leapidatasource".format(
        pkg_name = Settings.ds_package,
    ))
    return getattr(module, 'LeapiDataSource')

def get_datasource_instance():
    return get_datasource_cls(Settings.datasource_options)

def get_migrationhandler_cls():
    module = importlib.import_module("DataSource.{pkg_name}.migrationhandler".format(
        pkg_name = Settings.ds_package,
    ))
    return getattr(module, 'MigrationHandler')

def get_migrationhandler_instance():
    return get_migrationhandler_cls()(**Settings.migrationhandler_options)
