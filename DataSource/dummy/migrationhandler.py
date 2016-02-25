# -*- coding: utf-8 -*-

## @package EditorialModel.migrationhandler.dummy
# @brief A dummy migration handler
#
# According to it every modifications are possible
#


## Manage Model changes
class MigrationHandler(object):

    def __init__(self, debug=False):
        self.debug = debug

    ## @brief Record a change in the EditorialModel and indicate wether or not it is possible to make it
    # @note The states ( initial_state and new_state ) contains only fields that changes
    # @param em model : The EditorialModel.model object to provide the global context
    # @param uid int : The uid of the change EmComponent
    # @param initial_state dict | None : dict with field name as key and field value as value. Representing the original state. None mean creation of a new component.
    # @param new_state dict | None : dict with field name as key and field value as value. Representing the new state. None mean component deletion
    # @throw EditorialModel.exceptions.MigrationHandlerChangeError if the change was refused
    def register_change(self, em, uid, initial_state, new_state):
        if self.debug:
            print("\n##############")
            print("DummyMigrationHandler debug. Changes for component with uid %d :" % uid)
            if initial_state is None:
                print("Component creation (uid = %d): \n\t" % uid, new_state)
            elif new_state is None:
                print("Component deletion (uid = %d): \n\t" % uid, initial_state)
            else:
                field_list = set(initial_state.keys()).union(set(new_state.keys()))
                for field_name in field_list:
                    str_chg = "\t%s " % field_name
                    if field_name in initial_state:
                        str_chg += "'" + str(initial_state[field_name]) + "'"
                    else:
                        str_chg += " creating "
                    str_chg += " => "
                    if field_name in new_state:
                        str_chg += "'" + str(new_state[field_name]) + "'"
                    else:
                        str_chg += " deletion "
                    print(str_chg)
            print("##############\n")

    ## @brief Not usefull for the moment
    def register_model_state(self, em, state_hash):
        if self.debug:
            print("New EditorialModel state registered : '%s'" % state_hash)
