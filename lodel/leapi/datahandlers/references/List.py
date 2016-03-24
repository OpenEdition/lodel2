# -*- coding: utf-8 -*-
from lodel.editorial_model.components import EmClass
from lodel.leapi.datahandlers.reference import Reference


class List(Reference):

    ## @brief instanciates a list reference
    # @param emclasses list : linked emclasses objects
    # @param allowed list
    # @param internal bool
    # @param kwargs
    def __init__(self, emclasses, allowed=[], internal=False, **kwargs):
        self._refs = emclasses
        self._refs_class = list
        super().__init__(self, allowed=allowed, internal=internal, **kwargs)

    ## @brief adds a referenced element
    # @param emclass EmClass
    # @return bool
    def add_ref(self, emclass):
        if isinstance(emclass, EmClass):
            self._refs.append(emclass)
            return True
        return False