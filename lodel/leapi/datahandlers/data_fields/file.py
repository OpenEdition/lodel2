# -*- coding: utf-8 -*-
from ..data_field import DataField


class DataHandler(DataField):

    base_type = 'file'

    ## @brief a file field
    # @param upload_path str : None by default
    # @param **kwargs
    def __init__(self, upload_path=None, **kwargs):
        self.upload_path = upload_path
        super().__init__(ftype='file', **kwargs)

    def can_override(self, data_handler):
        if data_handler.__class__.base_type != self.__class__.base_type:
            return False
        return True
