# -*- coding: utf-8 -*-
from lodel.editorial_model.components import EmClass
from lodel.leapi.datahandlers.reference import Reference


class Set(Reference):

    ## @brief instanciates a set reference
    # @param emclasses list : List of EmClass objects
    # @param allowed bool
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, emclasses, allowed=True, internal=False, **kwargs):
        self._refs = set(emclasses)
        self._refs_class = set
        super().__init__(allowed=allowed, internal=internal, **kwargs)

    ## @brief adds a referenced element
    # @param emclass EmClass
    # @return bool
    def add_ref(self, emclass):
        if isinstance(emclass, EmClass):
            self._refs.add(emclass)
            return True
        return False