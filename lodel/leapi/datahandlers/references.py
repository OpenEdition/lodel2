# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.base_classes import Reference, MultipleRef, SingleRef

class Link(SingleRef): pass

## @brief Child class of MultipleRef where references are represented in the form of a python list
class List(MultipleRef):

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


## @brief Child class of MultipleRef where references are represented in the form of a python set
class Set(MultipleRef):

    ## @brief instanciates a set reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, allowed_classes=None, internal=False, **kwargs):
        super().__init__(allowed_classes=allowed_classes, internal=internal, **kwargs)

    ## @brief Check value
    # @param value *
    # @return tuple(value, exception)
    def _check_data_value(self, value):
        val, expt = super()._check_data_value()
        if not isinstance(expt, Exception):
            val = set(val)
        return val, expt


## @brief Child class of MultipleRef where references are represented in the form of a python dict
class Map(MultipleRef):

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
