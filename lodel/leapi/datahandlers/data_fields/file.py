# -*- coding: utf-8 -*-
from ..data_field import DataField


class EmDataField(DataField):

    ## @brief a file field
    # @param upload_path str : None by default
    # @param **kwargs
    def __init__(self, upload_path=None, **kwargs):
        self.upload_path = upload_path
        super(self.__class__, self).__init__(ftype='file', **kwargs)
