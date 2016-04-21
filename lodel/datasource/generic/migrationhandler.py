# -*- coding: utf-8 -*-

## @package lodel.datasource.migrationhandler.generic
# @brief A generic migration handler
#
# According to it, every moditification is possible
#


## Manage model changes
class GenericMigrationHandler(object):

    def __init__(self, debug=False):
        self.debug = debug

    ## @brief Records a change in the EditorialModel and indicates whether or not it is possible to make it
    # @note The states (initial_state and new_state) contains only fields that changes
    def register_change(self, em, uid, initial_state, new_state):
        if self.debug:
            print("\n##############")
            print("GenericMigrationHandler debug. Changes for component with uid %s :" % uid)
            if initial_state is None:
                print("Component creation (uid = %s): \n\t" % uid, new_state)
            elif new_state is None:
                print("Component deletion (uid = %s): \n\t" % uid, initial_state)
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
