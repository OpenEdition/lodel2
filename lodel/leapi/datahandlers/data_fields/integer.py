# -*- coding: utf-8 -*-
from ..data_field import FieldDataHandler


class DataHandler(FieldDataHandler):

    help = 'Basic integer field'
    base_type = 'int'

    def __init__(self, **kwargs):
        super().__init__(base_type='int', **kwargs)

    def _check_data_value(self, value):
        error = None
        try:
            value = int(value)
        except(ValueError, TypeError):
            error = TypeError("The value '%s' is not, and will never, be an integer" % value)
        return (value, error)

