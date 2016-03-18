# -*- coding: utf-8 -*-
from ..data_field import DataField


class EmDataField(DataField):
    help = 'Basic string (varchar) field. Default size is 64 characters'

    ## @brief A string field
    # @brief max_length int: The maximum length of this field
    def __init__(self, max_length=64, **kwargs):
        self.max_length = int(max_length)
        super().__init__(**kwargs)
