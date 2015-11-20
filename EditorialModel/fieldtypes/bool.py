#-*- coding: utf-8 -*-

from .generic import GenericFieldType


class EmFieldType(GenericFieldType):

    help = 'A basic boolean field'

    ftype = 'bool'

    ## @brief A char field
    # @brief max_length int : The maximum length of this field
    def __init__(self, **kwargs):
        super(EmFieldType, self).__init__(ftype='bool', **kwargs)

