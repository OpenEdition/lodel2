#-*- coding: utf-8 -*-

##@brief Abtract class for migration handlers
class DummyMigrationHandler(object):

    ##@brief Create a new migration handler given DB connection options
    def __init__(self, *args, **kwargs):
        pass
    
    ##@brief DB initialisation
    #@param emclass_list list : list of EmClasses concerned by this MH
    def init_db(self, emclass_list):
        pass
    
    ##@todo redefine
    def register_change(self, model, uid, initial_state, new_state):
        pass

    ##@todo redefine
    def register_model_state(self, em, state_hash):
        pass
    
