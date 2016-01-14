#-*- coding: utf-8 -*-

from . import char

class EmFieldType(char.EmFieldType):
    help = 'Automatic string field, defined as concatenation of other fields'

    def __init__(self, field_list, max_length, **kwargs):
        self._field_list = field_list
        super().__init__(internal='automatic', max_length = max_length)

    def _construct_data(self, lec, fname, datas, cur_value):
        ret = ''
        for fname in self._field_list:
            ret += datas[fname]
        return ret
