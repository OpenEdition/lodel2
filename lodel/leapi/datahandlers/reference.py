# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.field_data_handler import FieldDataHandler
from lodel.editorial_model.components import EmClass

class Reference(FieldDataHandler):

    ## @brief Instanciation
    # @param allowed bool
    # @param internal bool : if False, the field is not internal
    # @param **kwargs : other arguments
    def __init__(self, allowed=True, internal=False, **kwargs):
        self.allowed = allowed
        self.internal = internal
        if not self.is_ref_valid():
            raise ValueError("The target of the reference is not valid")
        super().__init__(internal=self.internal, **kwargs)

    ## @brief gets the target of the reference
    def get_relateds(self):
        return self._refs

    ## @brief checks if the target is valid
    def is_ref_valid(self):
        relateds = self.get_relateds()
        if not isinstance(relateds, self._refs_class):
            return False

        if isinstance(relateds, EmClass):
            relateds = [relateds]

        for related in relateds:
            if not isinstance(related, EmClass):
                return False

        return True

