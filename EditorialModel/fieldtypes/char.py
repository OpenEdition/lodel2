#-*- coding: utf-8 -*-

from .generic import SingleValueFieldType


class EmFieldType(SingleValueFieldType):

    help = 'Basic string (varchar) field. Take max_length=64 as option'

    ## @brief A char field
    # @brief max_length int : The maximum length of this field
    def __init__(self, max_length=64, **kwargs):
        self.max_length = max_length
        super().__init__(**kwargs)

