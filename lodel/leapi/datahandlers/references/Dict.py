# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.reference import Reference
from lodel.editorial_model.components import EmClass


class Dict(Reference):

    ## @brief instanciates a dict reference
    # @param emclasses dict : Dict of EmClass objects
    # @param allowed bool
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, emclasses, allowed=True, internal=False, **kwargs):
        self._refs = set(emclasses)
        self._refs_class = dict
        super().__init__(allowed=allowed, internal=internal, **kwargs)

    ## @brief checks if the given target is valid
    # @return bool
    def is_target_valid(self):
        relateds = self.get_relateds()

        if not isinstance(relateds, self._refs_class):
            return False

        for related in relateds.values():
            if not isinstance(related, EmClass):
                return False

        return True