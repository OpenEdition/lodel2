from django.conf import settings
from django.db import models

from EditorialModel.migrationhandler.django import DjangoMigrationHandler
from EditorialModel.migrationhandler.dummy import DummyMigrationHandler
from EditorialModel.model import Model
from EditorialModel.backend.json_backend import EmBackendJson


if not settings.LODEL_MIGRATION_HANDLER_TESTS:
    me = Model(EmBackendJson('EditorialModel/test/me.json'), migration_handler = DummyMigrationHandler(True))
    dmh = DjangoMigrationHandler('LodelTestInstance', settings.DEBUG)
    models = dmh.em_to_models(me)
elif settings.DEBUG:
    print("Making migrations tests, don't generate the models in the models.py file but within the migrations handler check process")


