# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.reference import Reference
from lodel.editorial_model.components import EmClass


class DataHandler(Reference):

    ## @brief instanciates a dict reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, allowed_classes=None, internal=False, **kwargs):
        super().__init__(allowed_classes=allowed_classes, internal=internal, **kwargs)

    ## @brief adds a referenced element
    # @param ref_name str : key of the item in the reference dict
    # @param emclass EmClass
    # @return bool
    def add_ref(self, ref_name, emclass):
        if isinstance(emclass, EmClass) and isinstance(ref_name, str):
            self._refs[ref_name] = emclass
            return True
        return False
