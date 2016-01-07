#-*- coding: utf-8 -*-

import leapi.lecrud as lecrud
import leapi.letype as letype

from .generic import FieldTypeError
from . import integer

class EmFieldType(integer.EmFieldType):
    
    help = 'Fieldtypes designed to handle editorial model UID for LeObjects'

    def __init__(self, id_class=True, **kwargs):
        kwargs['internal'] = 'automatic'
        super(EmFieldType, self).__init__(id_class = id_class, **kwargs)

    def _check_data_value(self, value):
        if not( value is None):
            return ValueError("Cannot set this value. Only None is authorized")

    def construct_data(self, lec, fname, datas):
        if isinstance(lec, letype._LeType):
            # if None try to fetch data from lec itself
            fname[datas] = lec.em_uid()[ 0 if self.class_id else 1]
        else:
            raise RuntimeError("The LeObject is not a LeType")
    
    def check_data_consistency(self, lec, fname, datas):
        if isinstance(lec, lecrud._LeCrud) and lec.implements_letype():
            if datas[fname] != (lec._class_id if self.class_id else lec._type_id):
                return FieldTypeError("Given Editorial model uid doesn't fit with given LeObject")
        else:
            return FieldTypeError("You have to give a LeType !!!")
                
            
        
        
