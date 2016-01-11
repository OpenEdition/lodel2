#-*- coding: utf-8 -*-

import leapi.lecrud as lecrud
import leapi.letype as letype

from .generic import FieldTypeError
from . import integer

class EmFieldType(integer.EmFieldType):
    
    help = 'Fieldtypes designed to handle editorial model UID for LeObjects'

    def __init__(self, is_id_class, **kwargs):
        self._is_id_class = is_id_class
        kwargs['internal'] = 'automatic'
        super(EmFieldType, self).__init__(is_id_class = is_id_class, **kwargs)

    def _check_data_value(self, value):
        return (value, None)

    def construct_data(self, lec, fname, datas):
        if self.is_id_class:
            if lec.implements_leclass():
                datas[fname] = lec._class_id
            else:
                datas[fname] = None
        else:
            if lec.implements_letype():
                datas[fname] = lec._type_id
            else:
                datas[fname] = None
        return datas[fname]
    
    def check_data_consistency(self, lec, fname, datas):
        if datas[fname] != (lec._class_id if self.is_id_class else lec._type_id):
            return FieldTypeError("Given Editorial model uid doesn't fit with given LeObject")
                
            
        
        
