#-*- coding: utf-8 -*-

from EditorialModel.fields import EmField

class EmFieldChar(EmField):
    
    ftype = 'char'
    help = 'Basic string (varchar) field. Take max_length=64 as option'
    
    ## @brief A char field
    # @brief max_length int : The maximum length of this field
    def __init__(self, max_length=64, **kwargs):
        self.max_length = max_length
        super(EmFieldChar, self).__init__(**kwargs)

fclass = EmFieldChar
