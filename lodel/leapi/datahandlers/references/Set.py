# -*- coding: utf-8 -*-
from ..reference import Reference


class Set(Reference):

    ## @brief instanciates a set reference
    # @param emclasses list : List of EmClass objects
    # @param allowed bool
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, emclasses, allowed=True, internal=False, **kwargs):
        self._target = set(emclasses)
        super().__init__(allowed=allowed, internal=internal, **kwargs)

