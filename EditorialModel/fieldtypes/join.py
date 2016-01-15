#-*- coding: utf-8 -*-

import warnings

from . import char

class EmFieldType(char.EmFieldType):
    help = 'Automatic string field, defined as concatenation of other fields'
    
    ## @brief Instanciate a fieldtype designed to concatenate fields
    # @param field_list list : fieldname list
    # @param glue str : separator
    # @param max_length int : Field max length
    def __init__(self, field_list, max_length, glue = ' ', **kwargs):
        self._field_list = field_list
        super().__init__(internal='automatic', max_length = max_length)

    def construct_data(self, lec, fname, datas, cur_value):
        ret = ''
        for fname in self._field_list:
            ret += datas[fname]
        if len(ret) > self.max_length:
            warnings.warn("Join field overflow. Truncating value")
            ret = [:self.max_length-1]
        return ret
