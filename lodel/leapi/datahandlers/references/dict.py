# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.field_data_handler import FieldValidationError
from lodel.leapi.datahandlers.reference import Reference
from lodel.editorial_model.components import EmClass


class DataHandler(Reference):

    ## @brief instanciates a dict reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, allowed_classes=None, internal=False, **kwargs):
        super().__init__(allowed_classes=allowed_classes, internal=internal, **kwargs)

    ## @brief Check value
    # @param value *
    # @return tuple(value, exception)
    def _check_data_value(self, value):
        if not isinstance(value, dict):
            return None, FieldValidationError("Values for dict fields should be dict")
        val, expt = super()._check_data_value(value.values())
        return (
                None if isinstance(expt, Exception) else value,
                expt)
