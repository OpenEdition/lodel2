#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent
from EditorialModel.fields import EmField
from EditorialModel.classes import EmClass
from EditorialModel.exceptions import *


## Represents groups of EmField associated with an EmClass
#
# EmClass fields representation is organised with EmFieldGroup
# @see EditorialModel::fields::EmField EditorialModel::classes::EmClass
class EmFieldGroup(EmComponent):

    ranked_in = 'class_id'

    ## EmFieldGroup instanciation
    def __init__(self, model, uid, name, class_id, string=None, help_text=None, date_update=None, date_create=None, rank=None):
        self.class_id = class_id
        self.check_type('class_id', int)
        super(EmFieldGroup, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)

    ## Check if the EmFieldGroup is valid
    # @throw EmComponentCheckError if fails
    def check(self):
        super(EmFieldGroup, self).check()
        em_class = self.model.component(self.class_id)
        if not em_class:
            raise EmComponentCheckError("class_id contains a non existing uid '"+str(self.class_id)+"'")
        if not isinstance(em_class, EmClass):
            raise EmComponentCheckError("class_id cointains an uid from a component that is not an EmClass but an "+type(em_class))

    ## Deletes a fieldgroup
    # @return True if the deletion is possible, False if not
    def delete_check(self):
        # all the EmField objects contained in this fieldgroup should be deleted first
        fieldgroup_fields = self.fields()
        if len(fieldgroup_fields) > 0:
            raise NotEmptyError("This Fieldgroup still contains fields. It can't be deleted then")
        return True

    ## Get the list of associated fields
    # if type_id, the fields will be filtered to represent selected fields of this EmType
    # @return A list of EmField instance
    def fields(self, type_id=0):
        if not type_id:
            fields = [field for field in self.model.components(EmField) if field.fieldgroup_id == self.uid]
        else:
            # for an EmType, fileds have to be filtered
            em_type = self.model.component(type_id)
            fields = []
            for field in self.model.components(EmField):
                if field.fieldgroup_id != self.uid or (field.optional and field.uid not in em_type.fields_list):
                    continue
                # don't include relational field if parent should not be included
                if field.rel_field_id:
                    parent = self.model.component(field.rel_field_id)
                    if parent.optional and parent.uid not in em_type.fields_list:
                        continue
                fields.append(field)

        return fields


class NotEmptyError(Exception):
    pass
