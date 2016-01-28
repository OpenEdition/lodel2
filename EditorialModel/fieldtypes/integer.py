#-*- coding: utf-8 -*-

from .generic import SingleValueFieldType


class EmFieldType(SingleValueFieldType):

    help = 'Basic integer field'

    ftype = 'int'

    def __init__(self, **kwargs):
        super(EmFieldType, self).__init__(ftype='int', **kwargs)

    def _check_data_value(self, value):
        error = None
        try:
            value = int(value)
        except (ValueError, TypeError):
            error = TypeError("the value '%s' is not, and will never be an integer" % value)
        return (value, error)
