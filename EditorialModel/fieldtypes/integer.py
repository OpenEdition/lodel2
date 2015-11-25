#-*- coding: utf-8 -*-

from .generic import GenericFieldType


class EmFieldType(GenericFieldType):

    help = 'Basic integer field'

    ftype = 'int'

    def __init__(self, **kwargs):
        if 'check_data_value' not in kwargs:
            kwargs['check_data_value'] = self.check_value
        super(EmFieldType, self).__init__(ftype='int', **kwargs)

    def check_value(self, value):
        error = None
        try:
            value = int(value)
        except ValueError:
            error = TypeError("the value '%s' is not, and will never be an integer" % value)
        return (value, error)
