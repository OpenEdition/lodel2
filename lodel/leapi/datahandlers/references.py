# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.base_classes import Reference, MultipleRef, SingleRef

class Link(SingleRef): pass

## @brief Child class of MultipleRef where references are represented in the form of a python list
class List(MultipleRef):

    ## @brief instanciates a list reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool
    # @param kwargs
    def __init__(self, max_length = None, **kwargs):
        super().__init__(**kwargs)

    ## @brief Check value
    # @param value *
    # @return tuple(value, exception)
    def _check_data_value(self, value):
        val, expt = super()._check_data_value()
        if not isinstance(expt, Exception):
            val = list(val)
        val, expt = super()._check_data_value(value.values())
        return val, expt


## @brief Child class of MultipleRef where references are represented in the form of a python set
class Set(MultipleRef):

    ## @brief instanciates a set reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    ## @brief Check value
    # @param value *
    # @return tuple(value, exception)
    def _check_data_value(self, value):
        val, expt = super()._check_data_value()
        if not isinstance(expt, Exception):
            val = set(val)
        val, expt = super()._check_data_value(value.values())
        return val, expt


## @brief Child class of MultipleRef where references are represented in the form of a python dict
class Map(MultipleRef):

    ## @brief instanciates a dict reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

## @brief This Reference class is designed to handler hierarchy with some constraint
class Hierarch(MultipleRef):
    
    ## @brief Instanciate a data handler handling hierarchical relation with constraints
    # @param back_reference tuple : Here it is mandatory to have a back ref (like a parent field)
    # @param max_depth int | None :  limit of depth
    # @param max_childs int | Nine : maximum number of childs by nodes
    def __init__(self, back_reference, max_depth = None, max_childs = None, **kwargs):
        super().__init__(back_reference = back_reference)
