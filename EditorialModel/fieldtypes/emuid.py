#-*- coding: utf-8 -*-

import leapi.lecrud as lecrud
import leapi.letype as letype

from .generic import FieldTypeError
from . import integer

class EmFieldType(integer.EmFieldType):
    
    help = 'Fieldtypes designed to handle editorial model UID for LeObjects'

    _construct_datas_deps = []

    def __init__(self, is_id_class, **kwargs):
        self._is_id_class = is_id_class
        kwargs['internal'] = 'automatic'
        super().__init__(is_id_class = is_id_class, **kwargs)

    def _check_data_value(self, value):
        return (value, None)

    def construct_data(self, lec, fname, datas, cur_value):
        ret = None
        if self.is_id_class:
            if lec.implements_leclass():
                ret = lec._class_id
        else:
            if lec.implements_letype():
                ret = lec._type_id
        return ret
    
    def check_data_consistency(self, lec, fname, datas):
        if datas[fname] != (lec._class_id if self.is_id_class else lec._type_id):
            return FieldTypeError("Given Editorial model uid doesn't fit with given LeObject")
                
            
        
        
