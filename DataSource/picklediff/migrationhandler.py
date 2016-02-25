#-*- coding: utf-8 -*-

from DataSource.dummy.migrationhandler import MigrationHandler

class MigrationHandler(MigrationHandler):

    def __init__(self, debug=False): pass

    def register_change(self, em, uid, initial_state, new_state): pass

    def register_model_state(self, em, state_hash): pass
