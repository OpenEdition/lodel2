#-*- coding: utf-8 -*-

from .generic import SingleValueFieldType


class EmFieldType(SingleValueFieldType):

    help = 'A basic boolean field'

    ftype = 'bool'

    ## @brief A boolean field
    # @brief max_length int : The maximum length of this field
    def __init__(self, **kwargs):
        if 'check_data_value' not in kwargs:
            kwargs['check_data_value'] = self.check_value
        super(EmFieldType, self).__init__(ftype='bool', **kwargs)

    def check_value(self, value):
        error = None
        try:
            value = bool(value)
        except (ValueError, TypeError):
            error = TypeError("the value '%s' is not, and will never be a boolean" % value)
        return (value, error)
