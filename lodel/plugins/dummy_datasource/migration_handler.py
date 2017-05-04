## @package lodel.plugins.dummy_datasource.migration_handler Migration handler of the datasource plugin. 
#
# The migration handler is here to report the changes made in the editorial model to the data source. 
# 
# For a database, it could be the creation/deletion of tables, the addition/deletion/change of certain columns, etc...
#
# We also have here the datasource initialization process, for the first use of it. The migration handler will then
# use the editorial model to generate the corresponding data storage. 

## @brief Abtract class for migration handlers
class DummyMigrationHandler(object):

    ## @brief Create a new migration handler given DB connection options
    def __init__(self, *args, **kwargs):
        pass
    
    ## @brief DB initialisation
    # @param emclass_list list : list of EmClasses concerned by this MH
    def init_db(self, emclass_list):
        pass
    
    ## @brief register a change in the editorial model
    # @param model EditorialModel
    # @param uid
    # @param initial_state
    # @param new_state
    # @todo redefine
    def register_change(self, model, uid, initial_state, new_state):
        pass

    ##
    # @param em EditorialModel
    # @param state_hash str
    # @todo redefine
    def register_model_state(self, em, state_hash):
        pass
    
