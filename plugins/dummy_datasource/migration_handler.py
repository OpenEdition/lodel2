#-*- coding: utf-8 -*-

##@brief Abtract class for migration handlers
class DummyMigrationHandler(object):
    def __init__(self, *args, **kwargs):
        pass
    
    def register_change(self, model, uid, initial_state, new_state):
        pass

    def register_model_state(self, em, state_hash):
        pass

