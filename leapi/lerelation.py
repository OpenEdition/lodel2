#-*- coding: utf-8 -*-

import copy

import EditorialModel.fieldtypes.leo as ft_leo
from . import lecrud
from . import leobject

## @brief Main class for relations
class _LeRelation(lecrud._LeCrud):

    ## @brief Handles the superior
    _lesup_fieldtype = {'lesup': ft_leo.EmFieldType(True)}
    ## @brief Handles the subordinate
    _lesub_fieldtype = {'lesub': ft_leo.EmFieldType(False) }
    ## @brief Stores the list of fieldtypes that are common to all relations
    _rel_fieldtypes = dict()

    def __init__(self, rel_id, **kwargs):
       pass

    @classmethod
    def sup_filter(self, leo):
        if isinstance(leo, leobject._LeObject):
            return ('lesup', '=', leo)

    @classmethod
    def sub_filter(self, leo):
        if isinstance(leo, leobject._LeObject):
            return ('lesub', '=', leo)

    @classmethod
    def fieldtypes(cls):
        rel_ft = dict()
        rel_ft.update(cls._lesup_fieldtype)
        rel_ft.update(cls._lesub_fieldtype)
        rel_ft.update(cls._rel_fieldtypes)
        if cls.implements_lerel2type():
            rel_ft.update(cls._rel_attr_fieldtypes)
        return rel_ft

    @classmethod
    def _prepare_relational_fields(cls, field):
        return lecrud.LeApiQueryError("Relational field '%s' given but %s doesn't is not a LeObject" % (field,
                                                                                                        cls.__name__))

    @classmethod
    def _prepare_filters(cls, filters_l):
        filters = list()
        res = list()
        rel = list()

        for filter_item in filters_l:
            if isinstance(filter_item, tuple):
                filters.append(filter_item)
            else:
                filter_item_data = filter_item.split(" ")
                if len(filter_item_data) == 3:
                    if filter_item_data[0] in cls._lesub_fieldtype.keys():
                        filter_item_data[2] = cls._lesub_fieldtype[filter_item_data[0]].construct_data(
                            cls,
                            filter_item_data[0],
                            {filter_item_data[0]: int(filter_item_data[2])}
                        )
                    elif filter_item_data[0] in cls._lesup_fieldtype.keys():
                        filter_item_data[2] = cls._lesup_fieldtype[filter_item_data[0]].construct_data(
                            cls,
                            filter_item_data[0],
                            {filter_item_data[0]: int(filter_item_data[2])}
                        )

                filters.append(tuple(filter_item_data))

        for field, operator, value in filters:
            if field.startswith('superior') or field.startswith('subordinate'):
                rel.append((field, operator, value))
            else:
                res.append((field, operator, value))

        return (res, rel)

## @brief Abstract class to handle hierarchy relations
class _LeHierarch(_LeRelation):
    def __init__(self, rel_id):
        pass

## @brief Abstract class to handle rel2type relations
class _LeRel2Type(_LeRelation):
    ## @brief Stores the list of fieldtypes handling relations attributes
    _rel_attr_fieldtypes = dict()
    pass
    
