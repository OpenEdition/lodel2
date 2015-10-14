#-*- coding: utf-8 -*-

from leobject.dyn import LeObject

## @brief Represent an EmClass data instance
class LeClass(LeObject):
    
    ## @brief Stores fieldtypes by field name
    _fieldtypes = dict()
    ## @brief Stores fieldgroups and the fields they contains
    _fieldgroups = dict()

    ## @brief Instanciate a new LeClass
    # @param model Model : The editorial model
    # @param datasource ? : The datasource
    def __init__(self, **kwargs):
        if self._cls_field is None:
            raise NotImplementedError("Abstract class")
        super(LeClass, self).__init__(**kwargs)
    
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
        
