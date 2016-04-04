# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.field_data_handler import FieldValidationError
from lodel.editorial_model.components import EmClass
from lodel.leapi.datahandlers.reference import Reference


class DataHandler(Reference):

    ## @brief instanciates a list reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool
    # @param kwargs
    def __init__(self, allowed_classes=None, internal=False, **kwargs):
        super().__init__(allowed_classes=allowed_classes, internal=internal, **kwargs)

    ## @brief Check value
    # @param value *
    # @return tuple(value, exception)
    def _check_data_value(self, value):
        val, expt = super()._check_data_value()
        if not isinstance(expt, Exception):
            val = list(val)
        return val, expt
