#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent
from EditorialModel.fieldtypes import EmField_boolean, EmField_char, EmField_integer, EmField_icon  # , get_field_type


## EmField (Class)
#
# Represents one data for a lodel2 document
class EmField(EmComponent):

    table = 'em_field'
    ranked_in = 'fieldgroup_id'
    _fields = [
        ('fieldtype', EmField_char),
        ('fieldgroup_id', EmField_integer),
        ('rel_to_type_id', EmField_integer),
        ('rel_field_id', EmField_integer),
        ('optional', EmField_boolean),
        ('internal', EmField_boolean),
        ('icon', EmField_icon)
    ]

    def __init__(self, datas, model):
        super(EmField, self).__init__(datas, model)

    ## @brief Delete a field if it's not linked
    # @return bool : True if deleted False if deletion aborded
    # @todo Check if unconditionnal deletion is correct
    def delete(self):
        return self.model.delete_component(self.uid)
