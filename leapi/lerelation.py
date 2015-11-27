#-*- coding: utf-8 -*-

import copy

import EditorialModel.fieldtypes.leo as ft_leo
from . import lecrud

## @brief Main class for relations
class _LeRelation(lecrud._LeCrud):
    
    ## @brief Handles the superior
    _lesup_fieldtype = {'lesup': ft_leo.EmFieldType(True)}
    ## @brief Handles the subordinate
    _lesub_fieldtype = {'lesub': ft_leo.EmFieldType(False) }
    ## @brief Stores the list of fieldtypes that are common to all relations
    _rel_fieldtypes = dict()
    ## @brief Stores the list of fieldtypes handling relations attributes
    _rel_attr_fieldtypes = dict()

    def __init__(self, rel_id, **kwargs):
       pass 
 
    @classmethod
    def fieldtypes(cls):
        rel_ft = dict()
        rel_ft.update(cls._lesup_fieldtype)
        rel_ft.update(cls._lesub_fieldtype)
        rel_ft.update(cls._rel_fieldtypes)
        rel_ft.update(cls._rel_attr_fieldtypes)
        return rel_ft

    @classmethod
    def _prepare_relational_fields(cls, field):
        return LeApiQueryError("Relational field '%s' given but %s doesn't is not a LeObject"%(field,cls.__name__))

            

## @brief Abstract class to handle hierarchy relations
class _LeHierarch(_LeRelation):
    def __init__(self, rel_id):
        pass

## @brief Abstract class to handle rel2type relations
class _LeRel2Type(_LeRelation):
    pass
    
