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
        self.id_relation = rel_id
    
    ## @brief Forge a filter to match the superior
    @classmethod
    def sup_filter(self, leo):
        if isinstance(leo, leobject._LeObject):
            return ('lesup', '=', leo)

    ## @brief Forge a filter to match the superior
    @classmethod
    def sub_filter(self, leo):
        if isinstance(leo, leobject._LeObject):
            return ('lesub', '=', leo)

    ## @return a dict with field name as key and fieldtype instance as value
    @classmethod
    def fieldtypes(cls):
        rel_ft = dict()
        rel_ft.update(cls._uid_fieldtype)

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
    ## @brief Prepare filters before sending them to the datasource
    # @param cls : Concerned class
    # @param filters_l list : List of filters
    # @return prepared and checked filters
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

    @classmethod
    ## @brief deletes a relation between two objects
    # @param filters_list list
    # @param target_class str
    def delete(cls, filters_list, target_class):
        filters, rel_filters = cls._prepare_filters(filters_list)
        if isinstance(target_class, str):
            target_class = cls.name2class(target_class)

        ret = cls._datasource.delete(target_class, filters)
        return True if ret == 1 else False

## @brief Abstract class to handle hierarchy relations
class _LeHierarch(_LeRelation):
    
    ## @brief Delete current instance from DB
    def delete(self):
        lecrud._LeCrud._delete(self)

## @brief Abstract class to handle rel2type relations
class _LeRel2Type(_LeRelation):
    ## @brief Stores the list of fieldtypes handling relations attributes
    _rel_attr_fieldtypes = dict()
    
    ## @brief Delete current instance from DB
    def delete(self):
        lecrud._LeCrud._delete(self)

    @classmethod
    def insert(cls, datas, classname):
        if 'nature' not in datas:
            datas['nature'] = None
        cls.name2class('LeCrud').insert(datas, classname)

    ## @brief Given a superior and a subordinate, returns the classname of the give rel2type
    # @param lesupclass LeClass : LeClass child class (can be a LeType or a LeClass child)
    # @param lesubclass LeType : A LeType child class
    # @return a name as string
    @staticmethod
    def relname(lesupclass, lesubclass):
        supname = lesupclass._leclass.__name__ if lesupclass.implements_letype() else lesupclass.__name__
        subname = lesubclass.__name__

        return "Rel_%s2%s" % (supname, subname)

