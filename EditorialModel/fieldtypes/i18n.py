#-*- coding: utf-8 -*-

import json

from Lodel.utils.mlstring import MlString

from .generic import MultiValueFieldType
from . import char

class EmFieldType(MultiValueFieldType):
    
    help = 'Fieldtype designed to handle translations'
    
    def __init__(self, value_max_length = 64, **args):
        args['keyname'] = 'lang'
        args['key_fieldtype'] = char.EmFieldType(max_length = 4)
        args['value_fieldtype'] = char.EmFieldType(value_max_length)
        super().__init__(**args)

    def _check_data_value(self, value):
        if isinstance(value, MlString):
            return (value, None)
        if isinstance(value, dict):
            for val in value.values():
                if not isinstance(val, str):
                    return (None, ValueError("Expected str as dict values. Bad dict : '%s'" % value))
            return (value, None)
        if isinstance(value, str):
            try:
                MlString(value)
                return (value, None)
            except ValueError:
                return (None, ValueError("Unable to load an MlString from value '%s'" % value))
        return (None, ValueError("Bad value : '%s'" % value))

    def construct_data(self, lec, fname, datas, cur_value):
        if not isinstance(cur_value, MlString):
            ret = MlString(cur_value)
        else:
            ret = cur_value
        if len(ret.get_default()) == 0 and len(ret.values()) > 0:
            ret.set_default(ret[list(ret.keys())[0]])
        return ret
