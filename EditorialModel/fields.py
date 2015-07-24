#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent
from EditorialModel.exceptions import *
import EditorialModel


## EmField (Class)
#
# Represents one data for a lodel2 document
class EmField(EmComponent):

    ranked_in = 'fieldgroup_id'

    ## Instanciate a new EmField
    # @todo define and test type for icon and fieldtype
    def __init__(self, model, uid, name, fieldgroup_id, fieldtype, optional=False, internal=False, rel_to_type_id=None, rel_field_id=None, icon='0', string=None, help_text=None, date_update=None, date_create=None, rank=None):

        self.fieldgroup_id = fieldgroup_id
        self.check_type('fieldgroup_id', int)
        self.fieldtype = fieldtype
        self.optional = optional
        self.check_type('optional', bool)
        self.internal = internal
        self.check_type('internal', bool)
        self.rel_to_type_id = rel_to_type_id
        self.check_type('rel_to_type_id', (int, type(None)))
        self.rel_field_id = rel_field_id
        self.check_type('rel_field_id', (int, type(None)))
        self.icon = icon
        super(EmField, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)

    ## Check if the EmField is valid
    # @return True if valid False if not
    def check(self):
        super(EmField, self).check()
        em_fieldgroup = self.model.component(self.fieldgroup_id)
        if not em_fieldgroup:
            raise EmComponentCheckError("fieldgroup_id contains a non existing uid : '%d'" % self.fieldgroup_id)
        if not isinstance(em_fieldgroup, EditorialModel.fieldgroups.EmFieldGroup):
            raise EmComponentCheckError("fieldgroup_id contains an uid from a component that is not an EmFieldGroup but a %s" % str(type(em_fieldgroup)))

    ## @brief Delete a field if it's not linked
    # @return bool : True if deleted False if deletion aborded
    # @todo Check if unconditionnal deletion is correct
    def delete(self):
        if self.model.delete_component(self.uid):
            return self.check()
        else:
            return False
