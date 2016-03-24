# -*- coding: utf-8 -*-
from ..reference import Reference


class List(Reference):

    ## @brief instanciates a list reference
    # @param emclasses list : linked emclasses objects
    def __init__(self, emclasses, allowed=True, internal=False, **kwargs):
        self._target = emclasses
        super().__init__(self, allowed=allowed, internal=internal, **kwargs)
