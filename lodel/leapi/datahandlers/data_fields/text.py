# -*- coding: utf-8 -*-
from ..data_field import DataField


class DataHandler(DataField):
    help = 'A text field (big string)'
    base_type = 'text'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(ftype='text', **kwargs)

    def can_override(self, data_handler):
        if data_handler.__class__.base_type != self.__class__.base_type:
            return False
        return True

    def can_override(self, data_handler):

        if data_handler.__class__.base_type != self.__class__.base_type:
            return False

        return True
