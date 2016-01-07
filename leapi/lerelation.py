#-*- coding: utf-8 -*-

import copy
import re

import EditorialModel.fieldtypes.leo as ft_leo
from . import lecrud
from . import leobject
from . import lefactory

## @brief Main class for relations
class _LeRelation(lecrud._LeCrud):

    _lesup_name = None
    _lesub_name = None
    ## @brief Stores the list of fieldtypes that are common to all relations
    _rel_fieldtypes = dict()

    def __init__(self, id_relation, **kwargs):
        super().__init__(id_relation, **kwargs)
    
    ## @brief Forge a filter to match the superior
    @classmethod
    def sup_filter(self, leo):
        if isinstance(leo, leobject._LeObject):
            return (self._lesup_name, '=', leo)

    ## @brief Forge a filter to match the superior
    @classmethod
    def sub_filter(self, leo):
        if isinstance(leo, leobject._LeObject):
            return (self._lesub_name, '=', leo)

    ## @return a dict with field name as key and fieldtype instance as value
    @classmethod
    def fieldtypes(cls):
        rel_ft = dict()
        rel_ft.update(cls._uid_fieldtype)

        rel_ft.update(cls._rel_fieldtypes)
        if cls.implements_lerel2type():
            rel_ft.update(cls._rel_attr_fieldtypes)
        return rel_ft

    ## @brief instanciate the relevant lodel object using a dict of datas
    @classmethod
    def object_from_data(cls, datas):
        if 'nature' in datas:
            return cls.name2class('LeHierarch')(**datas)
        return "To implement !"

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
        filters, rel_filters = super()._prepare_filters(filters_l)
        res_filters = list()
        for field, op, value in filters:
            if field in [cls._lesup_name, cls._lesub_name]:
                if isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError as e:
                        raise LeApiDataCheckError("Wrong value given for '%s'"%field)
                if isinstance(value, int):
                    value = cls.name2class('LeObject')(value)
            res_filters.append( (field, op, value) )
        return res_filters, rel_filters

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

    ## @brief move to the first rank
    # @return True in case of success, False in case of failure
    def move_first(self):
        return self.set_rank('first')

    ## @brief move to the last rank
    # @return True in case of success, False in case of failure
    def move_last(self):
        return self.set_rank('last')

    ## @brief move to the given rank defined by a shift step
    # @param step int : The step
    # @return True in case of success, False in case of failure
    # @throw ValueError if step is not castable into an integer
    def shift_rank(self, step):
        step = int(step)
        return self.set_rank(self.rank + step)
    
    ## @brief modify a relation rank
    # @param new_rank int|str : The new rank can be an integer > 1 or strings 'first' or 'last'
    # @return True in case of success, False in case of failure
    # @throw ValueError if step is not castable into an integer
    def set_rank(self, new_rank):
        max_rank = self.get_max_rank()
        try:
            new_rank = int(new_rank)
        except ValueError:
            if new_rank == 'first':
                new_rank = 1
            elif new_rank == 'last':
                new_rank = max_rank
            else:
                raise ValueError("The new rank can be an integer > 1 or strings 'first' or 'last', but %s given"%new_rank)

        if self.rank == new_rank:
            return True

        if new_rank < 1:
            if strict:
                raise ValueError("Rank must be >= 1, but %d given"%rank)
            new_rank = 1
        elif new_rank > max_rank:
            if strict:
                raise ValueError("Rank is too big (max_rank = %d), but %d given"%(max_rank,rank))
            new_rank = max_rank
        self._datasource.update_rank(self, new_rank)
    
    ## @returns The maximum assignable rank for this relation
    # @todo implementation
    def get_max_rank(self):
        max_rank_result = self.__class__.get(field_list=['rank'], order=[('rank', 'DESC')], limit=1)
        max_rank = int(max_rank_result[0].rank)
        return max_rank+1

## @brief Abstract class to handle hierarchy relations
class _LeHierarch(_LeRelation):
    
    ## @brief Delete current instance from DB
    def delete(self):
        lecrud._LeCrud._delete(self)

## @brief Abstract class to handle rel2type relations
class _LeRel2Type(_LeRelation):
    ## @brief Stores the list of fieldtypes handling relations attributes
    _rel_attr_fieldtypes = dict()
    
    ## @brief Stores the LeClass child class used as superior
    _superior_cls = None
    ## @biref Stores the LeType child class used as subordinate
    _subordinate_cls = None

    ## @brief Delete current instance from DB
    def delete(self):
        lecrud._LeCrud._delete(self)

    ## @brief Implements insert for rel2type
    # @todo checks when autodetecing the rel2type class
    @classmethod
    def insert(cls, datas, classname = None):
        #Set the nature
        if 'nature' not in datas:
            datas['nature'] = None
        if cls == cls.name2class('LeRel2Type') and classname is None:
            # autodetect the rel2type child class
            classname = relname(datas[self._lesup_name], datas[self._lesub_name])
        return super().insert(datas, classname)

    ## @brief Given a superior and a subordinate, returns the classname of the give rel2type
    # @param lesupclass LeClass : LeClass child class (not an instance) (can be a LeType or a LeClass child)
    # @param lesubclass LeType : A LeType child class (not an instance)
    # @return a name as string
    @staticmethod
    def relname(lesupclass, lesubclass):
        supname = lesupclass._leclass.__name__ if lesupclass.implements_letype() else lesupclass.__name__
        subname = lesubclass.__name__

        return "Rel_%s2%s" % (supname, subname)

