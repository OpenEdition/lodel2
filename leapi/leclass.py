#-*- coding: utf-8 -*-

import leapi



## @brief Represent an EmClass data instance
# @note Is not a derivated class of LeObject because the concrete class will be a derivated class from LeObject
class LeClass(object):

    ## @brief Stores fieldtypes by field name
    _fieldtypes = dict()
    ## @brief Stores relation with some LeType using rel2type fields. Key = rel2type fieldname value = LeType class
    _linked_types = dict()
    ## @brief Stores fieldgroups and the fields they contains
    _fieldgroups = dict()
    ## @brief Stores the EM uid
    _class_id = None
    ## @brief Stores the classtype
    _classtype = None

    ## @brief Instanciate a new LeClass
    # @note Abstract method
    # @param **kwargs
    def __init__(self, **kwargs):
        raise NotImplementedError("Abstract class")
