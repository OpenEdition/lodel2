# -*- coding: utf-8 -*-
from ..data_field import DataField


class DataHandler(DataField):
    help = 'A text field (big string)'
    ftype = 'text'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(ftype='text', **kwargs)
