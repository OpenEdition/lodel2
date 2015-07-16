#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent
import EditorialModel.fieldtypes as ftypes


## Represents groups of EmField associated with an EmClass
#
# EmClass fields representation is organised with EmFieldGroup
# @see EditorialModel::fields::EmField EditorialModel::classes::EmClass
class EmFieldGroup(EmComponent):

    ## The database table name
    table = 'em_fieldgroup'
    ranked_in = 'class_id'

    ## List of fields
    _fields = [('class_id', ftypes.EmField_integer)]

    ## Get the list of associated fields
    # @return A list of EmField instance
    def fields(self):
        pass