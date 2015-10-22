#-*- coding: utf-8 -*-

import leobject

## @brief Represent an EmClass data instance
# @note Is not a derivated class of LeObject because the concrete class will be a derivated class from LeObect
class LeClass(object):
    
    ## @brief Stores fieldtypes by field name
    _fieldtypes = dict()
    ## @brief Stores relation with some LeType using rel2type fields. Key = rel2type fieldname value = LeType class
    _linked_types = dict()
    ## @brief Stores fieldgroups and the fields they contains
    _fieldgroups = dict()
    ## @brief Stores the EM uid
    _class_id = None

    ## @brief Instanciate a new LeClass
    # @note Abstract method
    # @param **kwargs
    def __init__(self, **kwargs):
        raise NotImplementedError("Abstract class")
    
    ## @brief Get the linked objects
    # @return an array of LeType derivated class instance
    def linked(self):
        pass
    
    ## @brief Link this class with an LeObject
    # @param leo LeObject : The object to be linked with
    # @return True if success False allready done
    # @throw A Leo exception if the link is not allowed
    def link_to(self, leo):
        pass
        
