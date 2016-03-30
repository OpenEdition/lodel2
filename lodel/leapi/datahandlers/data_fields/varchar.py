# -*- coding: utf-8 -*-
from ..data_field import DataField


class DataHandler(DataField):

    help = 'Basic string (varchar) field. Default size is 64 characters'
    base_type = 'char'

    ## @brief A string field
    # @brief max_length int: The maximum length of this field
    def __init__(self, max_length=64, **kwargs):
        self.max_length = int(max_length)
        super().__init__(**kwargs)

    def can_override(self, data_handler):

        if data_handler.__class__.base_type != self.__class__.base_type:
            return False

        if data_handler.max_length != self.max_length:
            return False

        return True
