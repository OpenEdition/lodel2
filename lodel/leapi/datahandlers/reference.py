# -*- coding: utf-8 -*-
from .field_data_handler import FieldDataHandler


class Reference(FieldDataHandler):

    ## @brief Instanciation
    # @param allowed bool
    # @param internal bool : if False, the field is not internal
    # @param **kwargs : other arguments
    def __init__(self, allowed=True, internal=False, **kwargs):
        self.allowed = allowed
        self.internal = internal
        super().__init__(internal=self.internal, **kwargs)

    ## @brief gets the target of the reference
    def get_target(self):
        return self._target
