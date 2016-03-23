# -*- coding: utf-8 -*-
import warnings
from .varchar import EmDataField as VarcharDataField


class EmDataField(VarcharDataField):

    help = 'Automatic string field, designed to use the str % operator to build its content'

    ## @brief Build its content with a field list and a format string
    # @param format_string str
    # @param max_length int : the maximum length of the handled value
    # @param field_list list : List of field to use
    # @param **kwargs
    def __init__(self, format_string, field_list, max_length, **kwargs):
        self._field_list = field_list
        self._format_string = format_string
        super(self.__class__, self).__init__(internal='automatic', max_length=max_length)
