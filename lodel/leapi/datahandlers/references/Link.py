# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.reference import Reference
from lodel.editorial_model.components import EmClass


class Link(Reference):

    ## @brief instanciates a link reference
    # @param emclass EmClass : linked object
    # @param allowed bool
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, emclass, allowed=True, internal=False, **kwargs):
        self._refs = emclass
        self._refs_class = EmClass
        super().__init__(allowed=allowed, internal=internal, **kwargs)
