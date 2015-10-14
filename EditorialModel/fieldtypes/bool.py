#-*- coding: utf-8 -*-

from EditorialModel.fieldtypes.generic import GenericFieldType

class EmFieldBool(GenericFieldType):

    help = 'A basic boolean field'

    ## @brief A char field
    # @brief max_length int : The maximum length of this field
    def __init__(self, **kwargs):
        super(EmFieldBool, self).__init__(ftype='bool',**kwargs)

