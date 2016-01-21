#-*- coding: utf-8 -*-

import leapi

from leapi.leobject import _LeObject

## @brief Represent an EmClass data instance
# @note Is not a derivated class of LeObject because the concrete class will be a derivated class from LeObject
class _LeClass(_LeObject):

    ## @brief Stores fieldtypes by field name
    _fieldtypes = dict()
    ## @brief Stores authorized link2type
    _linked_types = list()
    ## @brief Stores fieldgroups and the fields they contains
    _fieldgroups = dict()
    ## @brief Stores the EM uid
    _class_id = None
    ## @brief Stores the classtype
    _classtype = None

    @classmethod
    def fieldtypes(cls, complete=True):
        ret = dict()
        if complete:
            ret.update(super().fieldtypes())
        ret.update(cls._fieldtypes)
        return ret

    @classmethod
    def fieldlist(cls, complete=True):
        return list(cls.fieldtypes(complete).keys())

    @classmethod
    def get(cls, query_filters, field_list=None, order=None, group=None, limit=None, offset=0):
        query_filters.append(('class_id', '=', cls._class_id))
        return super().get(query_filters, field_list, order=order, group=group, limit=limit, offset=offset)

    @classmethod
    def leo_class(cls):
        return cls
