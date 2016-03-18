# -*- coding: utf-8 -*-
from ..data_field import DataField


class EmDataField(DataField):
    help = 'A text field (big string)'
    ftype = 'text'

    def __init__(self):
        super(Text, self).__init__(ftype='text', **kwargs)
