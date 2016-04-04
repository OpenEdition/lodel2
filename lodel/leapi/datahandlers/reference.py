# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.field_data_handler import FieldDataHandler, FieldValidationError
from lodel.editorial_model.components import EmClass


class Reference(FieldDataHandler):

    ## @brief Instanciation
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool : if False, the field is not internal
    # @param **kwargs : other arguments
    def __init__(self, allowed_classes = None, internal=False, **kwargs):
        self.__allowed_classes = None if allowed_classes is None else set(allowed_classes)
        super().__init__(internal=internal, **kwargs)

    ## @brief Check value
    # @param value *
    # @return tuple(value, exception)
    def _check_data_value(self, value):
        if isinstance(value, EmClass):
            value = [value]
        for elt in value:
            if not issubclass(elt.__class__, EmClass):
                return None, FieldValidationError("Some elements of this references are not EmClass instances")
            if self.__allowed_classes is not None:
                if not isinstance(elt, self.__allowed_classes):
                    return None, FieldValidationError("Some element of this references are not valids (don't fit with allowed_classes")
        return value

