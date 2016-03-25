# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.field_data_handler import FieldDataHandler
from lodel.editorial_model.components import EmClass


class Reference(FieldDataHandler):

    ## @brief Instanciation
    # @param allowed list
    # @param internal bool : if False, the field is not internal
    # @param **kwargs : other arguments
    def __init__(self, allowed=[], internal=False, **kwargs):
        self.allowed = allowed
        self.internal = internal
        super().__init__(internal=self.internal, **kwargs)

    ## @brief gets the target of the reference
    def get_relateds(self):
        return self._refs

    ## @brief checks if the target is valid

    def check_data_value(self, value):

        if not isinstance(value, self._refs_class):
            return (value, "The reference should be an instance of %s, %s gotten" % (self._refs_class, value.__class__))

        if isinstance(value, EmClass):
            value = [value]

        if isinstance(value, dict):
            ref_values = value.values()

        for related in value:
            if not isinstance(related, EmClass):
                return (value, "The reference %s should be an instance of EmClass, %s gotten" % (related.display_name, related.__class__))

        return (value, None)
