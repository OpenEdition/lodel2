# -*- coding: utf-8 -*-

## Manage Model changes
class DummyMigrationHandler(object):
    
    ## @brief Record a change in the EditorialModel and indicate wether or not it is possible to make it
    # @note The states ( initial_state and new_state ) contains only fields that changes
    # @param uid int : The uid of the change EmComponent
    # @param initial_state dict : dict with field name as key and field value as value representing the original state
    # @param new_state dict : dict with field name as key and field value as value representing the new state
    # @return True if the modification is allowed False if not.
    def register_change(self, uid, initial_state, new_state):
        return True
        
