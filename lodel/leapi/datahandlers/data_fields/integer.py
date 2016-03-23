# -*- coding: utf-8 -*-
from ..data_field import DataField


class EmDataField(DataField):

    help = 'Basic integer field'
    ftype = 'int'

    def __init__(self, **kwargs):
        super().__init__(ftype='int', **kwargs)

    def _check_data_value(self, value):
        error = None
        try:
            value = int(value)
        except(ValueError, TypeError):
            error = TypeError("The value '%s' is not, and will never, be an integer" % value)
        return (value, error)
