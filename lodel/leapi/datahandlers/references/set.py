# -*- coding: utf-8 -*-
from lodel.editorial_model.components import EmClass
from lodel.leapi.datahandlers.reference import Reference


class DataHandler(Reference):

    ## @brief instanciates a set reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, allowed_classes = None, internal=False, **kwargs):
        super().__init__(allowed_classes=allowed_classes, internal=internal, **kwargs)

    ## @brief adds a referenced element
    # @param emclass EmClass
    # @return bool
    def add_ref(self, emclass):
        if isinstance(emclass, EmClass):
            self._refs.add(emclass)
            return True
        return False
