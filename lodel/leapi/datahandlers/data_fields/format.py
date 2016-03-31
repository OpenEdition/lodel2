# -*- coding: utf-8 -*-
import warnings
from .varchar import DataHandler as VarcharDataHandler


class DataHandler(VarcharDataHandler):

    help = 'Automatic string field, designed to use the str % operator to build its content'
    base_type = 'char'

    ## @brief Build its content with a field list and a format string
    # @param format_string str
    # @param max_length int : the maximum length of the handled value
    # @param field_list list : List of field to use
    # @param **kwargs
    def __init__(self, format_string, field_list, max_length, **kwargs):
        self._field_list = field_list
        self._format_string = format_string
        super().__init__(internal='automatic', max_length=max_length)

    def can_override(self, data_handler):
        if not super().can_override(data_handler):
            return False

        if data_handler.max_length != self.max_length:
            return False

        return True