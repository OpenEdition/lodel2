#-*- coding: utf-8 -*-
from lodel.leapi.datahandlers.reference import Reference
from lodel.editorial_model.components import EmClass

## @brief This class represent a data_handler for multiple references to another object
class MultipleRef(Reference):
    
    def __init__(self, allowed_classes = None, **kwargs):
        super().__init__(allowed_classes = allowed_classes
    
