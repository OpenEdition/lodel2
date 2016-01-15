#-*- coding: utf-8 -*-

import warnings

from . import char

class EmFieldType(char.EmFieldType):
    help = 'Automatic string field, designed to use the str % operator to build its content'

    ## @brief Build its content with a field list and a format string
    # @param format_string str :  
    # @param field_list list : List of field to use
    def __init__(self, format_string, field_list, max_length, **kwargs):
        self._field_list = field_list
        self._format_string = format_string
        super().__init__(internal='automatic', max_length = max_length)

    def construct_data(self, lec, fname, datas, cur_value):
        ret = self._format_string % tuple([ datas[fname] for fname in self._field_list ])
        if len(ret) > self.max_length:
            warnings.warn("Format field overflow. Truncating value")
            ret = [:self.max_length-1]
        return ret
