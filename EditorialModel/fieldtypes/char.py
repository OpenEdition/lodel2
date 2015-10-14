#-*- coding: utf-8 -*-

from EditorialModel.fieldtypes.generic import GenericFieldType

class EmFieldType(GenericFieldType):

    help = 'Basic string (varchar) field. Take max_length=64 as option'

    ## @brief A char field
    # @brief max_length int : The maximum length of this field
    def __init__(self, max_length=64, **kwargs):
        self.max_length = max_length
        super(EmFieldType, self).__init__(ftype = 'char', **kwargs)

