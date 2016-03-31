# -*- coding: utf-8 -*-
from ..data_field import DataField


class DataHandler(DataField):

    help = 'A datetime field. Take two boolean options now_on_update and now_on_create'
    base_type = 'datetime'

    ## @brief A datetime field
    # @param now_on_update bool : If true, the date is set to NOW on update
    # @param now_on_create bool : If true, the date is set to NEW on creation
    # @param **kwargs
    def __init__(self, now_on_update=False, now_on_create=False, **kwargs):
        self.now_on_update = now_on_update
        self.now_on_create = now_on_create
        super().__init__(**kwargs)

    def can_override(self, data_handler):

        if data_handler.__class__.base_type != self.__class__.base_type:
            return False

        return True