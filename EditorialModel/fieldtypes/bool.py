#-*- coding: utf-8 -*-

from EditorialModel.fields import EmField


class EmFieldBool(EmField):

    ftype = 'bool'
    help = 'A basic boolean field'

    ## @brief A char field
    # @brief max_length int : The maximum length of this field
    def __init__(self, **kwargs):
        super(EmFieldBool, self).__init__(**kwargs)

fclass = EmFieldBool
