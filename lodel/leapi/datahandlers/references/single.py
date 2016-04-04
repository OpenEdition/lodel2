#-*- coding: utf-8 -*-
from lodel.leapi.datahandlers.reference import Reference
from lodel.editorial_model.components import EmClass

## @brief This class represent a data_handler for single reference to another object
class SingleRef(Reference):
    
    def __init__(self, allowed_classes = None, **kwargs):
        super().__init__(allowed_classes = allowed_classes
 
    def _check_data_value(self, value):
        val, expt = super()._check_data_value(value)
        if not isinstance(expt, Exception):
            if len(val) > 1:
               return None, FieldValidationError("Only single values are allowed for SingleRef fields")
        return val, expt
    
