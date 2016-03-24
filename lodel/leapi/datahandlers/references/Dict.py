# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.reference import Reference
from lodel.editorial_model.components import EmClass


class Dict(Reference):

    ## @brief instanciates a dict reference
    # @param emclasses dict : Dict of EmClass objects
    # @param allowed list
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, emclasses, allowed=[], internal=False, **kwargs):
        self._refs = set(emclasses)
        self._refs_class = dict
        super().__init__(allowed=allowed, internal=internal, **kwargs)

    ## @brief checks if the given target is valid
    # @return bool
    def _check_data_value(self, value):
        relateds = self.get_relateds()

        if not isinstance(relateds, self._refs_class):
            return

        for related in relateds.values():
            if not isinstance(related, EmClass):
                return False

        return True

    ## @brief adds a referenced element
    # @param ref_name str : key of the item in the reference dict
    # @param emclass EmClass
    # @return bool
    def add_ref(self, ref_name, emclass):
        if isinstance(emclass, EmClass) and isinstance(ref_name, str):
            self._refs[ref_name] = emclass
            return True
        return False