#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent
from EditorialModel.fieldtypes import EmField_boolean, EmField_char, EmField_integer, EmField_icon  # , get_field_type


## EmField (Class)
#
# Represents one data for a lodel2 document
class EmField(EmComponent):

    ranked_in = 'fieldgroup_id'

    def __init__(self, model, uid, name, fieldgroup_id, fieldtype, optional = False, internal = False, rel_to_type_id = None, rel_field_id = None, icon = '0', string = None, help_text = None, date_update = None, date_create = None, rank = None):
        self.fieldgroup_id = fieldgroup_id
        self.fieldtype = fieldtype
        self.optional = optional
        self.internal = internal
        self.rel_to_type_id = rel_to_type_id
        self.rel_field_id = rel_field_id
        self.icon = icon
        super(EmField, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)

    ## Check if the EmField is valid
    # @return True if valid False if not
    def check(self):
        super(EmField, self).check()
        return True

    ## @brief Delete a field if it's not linked
    # @return bool : True if deleted False if deletion aborded
    # @todo Check if unconditionnal deletion is correct
    def delete(self):
        if self.model.delete_component(self.uid):
            return self.check()
        else:
            return False
