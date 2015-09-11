from django.db import models

from EditorialModel.migrationhandler.django import DjangoMigrationHandler
from EditorialModel.migrationhandler.dummy import DummyMigrationHandler
from EditorialModel.model import Model
from EditorialModel.backend.json_backend import EmBackendJson


me = Model(EmBackendJson('EditorialModel/test/me.json'), migration_handler = DummyMigrationHandler(True))

dmh = DjangoMigrationHandler()

models = dmh.me_to_models(me,'LodelTestInstance', 'LodelTestInstance.models')


