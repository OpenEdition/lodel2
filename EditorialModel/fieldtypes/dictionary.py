#-*- coding: utf-8 -*-

from .generic import MultiValueFieldType
from . import char


class EmFieldType(MultiValueFieldType):
    
    help = 'Fieldtype designed to handle translations'
    
    def __init__(self, value_max_length = 64, **args):
        args['keyname'] = 'key'
        args['key_fieldtype'] = char.EmFieldType(max_length = 4)
        args['value_fieldtype'] = char.EmFieldType(value_max_length)
        super().__init__(**args)
