# -*- coding: utf-8 -*-
from ..data_field import DataField


class EmDataField(DataField):

    help = 'A basic boolean field'
    ftype = 'bool'

    ## @brief A boolean field
    def __init__(self, **kwargs):
        if 'check_data_value' not in kwargs:
            kwargs['check_data_value'] = self.check_value
        super(self.__class__, self).__init__(ftype='bool', **kwargs)

    def _check_data_value(self, value):
        error = None
        try:
            value = bool(value)
        except(ValueError, TypeError):
            error = TypeError("The value '%s' is not, and will never, be a boolean" % value)
        return (value, error)
