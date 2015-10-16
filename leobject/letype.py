#-*- coding: utf-8 -*-

from leobject.leclass import LeClass

## @brief Represent an EmType data instance
# @note Is not a derivated class of LeClass because the concrete class will be a derivated class from LeClass
class LeType(object):
    
    ## @brief Stores selected fields with key = name
    _fields = list()
    ## @brief Stores the class of LeClass
    _leclass = None
    
    ## @brief Instanciate a new LeType
    # @param lodel_id : The lodel id
    # @param **kwargs : Datas used to populate a LeType
    def __init__(self, lodel_id, **kwargs):
        if self._leclass is None:
            raise NotImplementedError("Abstract class")

        self.lodel_id = lodel_id
        ## Populate the object from the datas received in kwargs
        for name, value in kwargs.items():
            if name not in self._fields:
                raise AttributeError("No such field '%s' for %s"%(name, self.__class__.__name__)
            setattr(self, name, value)
    
    ## @brief Insert a new LeType in the datasource
    # @param **datas : A dict containing the datas
    # @return The lodel id of the new LeType or False
    # @thorw A leo exception if invalid stuff
    # @throw InvalidArgumentError if invalid argument
    @classmethod
    def insert(cls, **datas):
        #check datas
        autom_fields = ['lodel_id', 'typename', 'classname' ]
        for forbiden in autom_fields:
            if forbiden in datas:
                raise AttributeError("Not allowed to give explicitly '%s' to insert method"%(forbiden))
        self.check_datas(datas)

        super(LeType, self).insert(typename=self.__class__.__name__, classname=self._leclass.__name__, **datas)
        pass
    
    ## @brief Delete a LeType from the datasource
    # @param lodel_id int : The lodel_id identifying the LeType
    # @param return True if deleted False if not existing
    # @throw InvalidArgumentError if invalid parameters
    # @throw Leo exception if the lodel_id identify an object from another type
    @classmethod
    def c_delete(cls, lodel_id):
        pass
    
    ## @brief Update some objects in db
    # @param lodel_id_l list : A list of lodel_id to update
    # @param data dict : Represent the datas to update
    # @return True if updated else False
    # @throw InvalidArgumentError if invalid parameters
    # @throw other Leo exceptions
    @classmethod
    def c_update(cls, lodel_id_l, datas):
        pass
    
    ## @brief Check that datas are valid for this type
    # @param datas dict : key == field name value are field values
    # @throw If the datas are not valids
    @classmethod
    def check_datas(cls, datas):
        for dname, dval in datas.items():
            if dname not in cls._fields:
                raise AttributeError("No such field '%s' for %s"%(dname, self.__class__.__name__)
            cls._fields[dname].check_or_raise(dval)
                

    ## @brief Implements the automatic checks of attributes
    # @note Run data check from fieldtypes if we try to modify an field attribute of the LeType
    # @param name str : The attribute name
    # @param value * : The value
    def __setattr__(self, name, value):
        if name in self._fields.keys():
            self._fields[name].check_or_raise(value)
        return super(LeType, self).__setattr__(name, value)

    ## @brief Delete the LeType
    # @return True if deleted False if not
    def delete(self):
        return self.__class__.delete(self.lodel_id)
    
    ## @brief Update a LeType
    # @return True if ok else False
    def update(self):
        return self.__class__.update(self.lodel_id, self._datas)
        
    ## @brief Fetch superiors
    # @param nature str : The relation nature
    # @return if no nature given return a dict with nature as key and arrays of LeObject as value. Else return an array of LeObject
    def superiors(self, nature = None):
        pass

    ## @brief Fetch subordinates
    # @param nature str : The relation nature
    # @return if no nature given return a dict with nature as key and arrays of LeObject as value. Else return an array of LeObject
    def subordinates(self, nature = None):
        pass

    ## @brief Add a superior
    # @param nature str : The raltion nature
    # @param leo LeObject : The superior
    # @param return True if done False if already done
    # @throw A Leo exception if trying to link with an invalid leo
    # @throw InvalidArgumentError if invalid argument
    def add_superior(self, nature, leo):
        pass
    