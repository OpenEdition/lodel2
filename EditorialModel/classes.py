# -*- coding: utf-8 -*-

## @file classes.py
# @see EditorialModel::classes::EmClass

from EditorialModel.components import EmComponent
import EditorialModel.fieldtypes as ftypes


## @brief Manipulate Classes of the Editorial Model
# Create classes of object.
# @see EmClass, EmType, EmFieldGroup, EmField
# @todo sortcolumn handling
class EmClass(EmComponent):

    table = 'em_class'
    ranked_in = 'classtype'

    ## @brief Specific EmClass fields
    # @see EditorialModel::components::EmComponent::_fields
    _fields = [
        ('classtype', ftypes.EmField_char),
        ('icon', ftypes.EmField_icon),
        ('sortcolumn', ftypes.EmField_char)
    ]

    @property
    ## @brief Return the table name used to stores data on this class
    def class_table_name(self):
        return self.name


    ## Retrieve list of the field_groups of this class
    # @return A list of fieldgroups instance
    def fieldgroups(self):
        pass

    ## Retrieve list of fields
    # @return fields [EmField]:
    def fields(self):
        fieldgroups = self.fieldgroups()
        fields = []
        for fieldgroup in fieldgroups:
            fields += fieldgroup.fields()
        return fields

    ## Retrieve list of type of this class
    # @return types [EmType]:
    def types(self):
        pass

    ## Add a new EmType that can ben linked to this class
    # @param  em_type EmType: type to link
    # @return success bool: done or not
    def link_type(self, em_type):
        pass


    ## Retrieve list of EmType that are linked to this class
    #  @return types [EmType]:
    def linked_types(self):
        pass