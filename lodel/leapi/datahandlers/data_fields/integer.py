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

    def can_override(self, data_handler):
        if data_handler.__class__.base_type != self.__class__.base_type:
            return False
        return True
