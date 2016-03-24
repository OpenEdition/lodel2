# -*- coding: utf-8 -*-
from ..reference import Reference


class Link(Reference):

    ## @brief instanciates a link reference
    # @param emclass EmClass : linked object
    # @param allowed bool
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, emclass, allowed=True, internal=False, **kwargs):
        self._target = emclass
        super().__init__(allowed=allowed, internal=internal, **kwargs)


