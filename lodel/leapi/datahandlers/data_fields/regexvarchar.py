# -*- coding: utf-8 -*-
import re
from .varchar import DataHandler as VarcharDataHandler


class DataHandler(VarcharDataHandler):

    help = 'String field validated with a regex. Takes two options : max_length and regex'
    base_type = 'char'

    ## @brief A string field validated by a regex
    # @param regex str : a regex string (passed as argument to re.compile())
    # @param max_length int : the max length for this field (default : 10)
    # @param **kwargs
    def __init__(self, regex='', max_length=10, **kwargs):
        self.regex = regex
        self.compiled_re = re.compile(regex)  # trigger an error if invalid regex

        super(self.__class__, self).__init__(max_length=max_length, **kwargs)

    def _check_data_value(self, value):
        error = None
        if not self.compiled_re.match(value):
            value = ''
            error = TypeError('"%s" doesn\'t match the regex "%s"' % (value, self.regex))
        return value, error

    def can_override(self, data_handler):
        if not super().can_override(data_handler):
            return False

        if data_handler.max_length != self.max_length:
            return False
        return True