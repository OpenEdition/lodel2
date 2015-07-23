#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent
import EditorialModel.fieldtypes as ftypes
from EditorialModel.fields import EmField


## Represents groups of EmField associated with an EmClass
#
# EmClass fields representation is organised with EmFieldGroup
# @see EditorialModel::fields::EmField EditorialModel::classes::EmClass
class EmFieldGroup(EmComponent):

    ranked_in = 'class_id'

    ## List of fields
    _fields = [('class_id', ftypes.EmField_integer)]

    ## Deletes a fieldgroup
    # @return True if the deletion is a success, False if not
    def delete(self):
        # all the EmField objects contained in this fieldgroup should be deleted first
        fieldgroup_fields = self.fields()
        if len(fieldgroup_fields) > 0:
            raise NotEmptyError("This Fieldgroup still contains fields. It can't be deleted then")
        # then we delete this fieldgroup
        return self.model.delete_component(self.uid)

    ## Get the list of associated fields
    # @return A list of EmField instance
    def fields(self):
        fields = [field for field in self.model.components(EmField) if field.fieldgroup_id == self.uid]
        return fields

class NotEmptyError(Exception):
    pass
