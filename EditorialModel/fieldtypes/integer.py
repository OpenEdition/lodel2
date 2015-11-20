#-*- coding: utf-8 -*-

from .generic import GenericFieldType


class EmFieldType(GenericFieldType):

    help = 'Basic integer field'

    ftype = 'int'

    @staticmethod
    def check_fun(value):
        try:
            int(value)
        except ValueError:
            raise TypeError("the value '%s' is not, and will never be an integer" % value)

    def __init__(self, **kwargs):
        if 'check_function' not in kwargs:
            kwargs['check_function'] = self.check_fun
        super(EmFieldType, self).__init__(ftype='int', **kwargs)
