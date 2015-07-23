# -*- coding: utf-8 -*-

## @file components.py
# Defines the EditorialModel::components::EmComponent class and the EditorialModel::components::ComponentNotExistError exception class

import datetime

import logging
import EditorialModel.fieldtypes as ftypes
from collections import OrderedDict

logger = logging.getLogger('Lodel2.EditorialModel')


## This class is the mother class of all editorial model objects
#
# It gather all the properties and mechanism that are common to every editorial model objects
# @see EditorialModel::classes::EmClass, EditorialModel::types::EmType, EditorialModel::fieldgroups::EmFieldGroup, EditorialModel::fields::EmField
# @pure
class EmComponent(object):

    ## Used by EmComponent::modify_rank
    ranked_in = None

    ## Read only properties
    _ro_properties = ['date_update', 'date_create', 'uid', 'rank', 'deleted']

    ## @brief List fields name and fieldtype
    #
    # This is a list that describe database fields common for each EmComponent child classes.
    # A database field is defined here by a tuple(name, type) with name a string and type an EditorialModel.fieldtypes.EmFieldType
    # @warning The EmFieldType in second position in the tuples must be a class type and not a class instance !!!
    # @see EditorialModel::classes::EmClass::_fields EditorialModel::fieldgroups::EmFieldGroup::_fields EditorialModel::types::EmType::_fields EditorialModel::fields::EmField::_fields
    _fields = [
        ('uid', ftypes.EmField_integer),
        ('name', ftypes.EmField_char),
        ('rank', ftypes.EmField_integer),
        ('date_update', ftypes.EmField_date),
        ('date_create', ftypes.EmField_date),
        ('string', ftypes.EmField_mlstring),
        ('help', ftypes.EmField_mlstring)
    ]

    ## Instaciate an EmComponent
    # @param id_or_name int|str: name or id of the object
    # @throw TypeError if id_or_name is not an integer nor a string
    # @throw NotImplementedError if called with EmComponent
    def __init__(self, data, model):
        if type(self) == EmComponent:
            raise NotImplementedError('Abstract class')

        ## @brief An OrderedDict storing fields name and values
        # Values are handled by EditorialModel::fieldtypes::EmFieldType
        # @warning \ref _fields instance property is not the same than EmComponent::_fields class property. In the instance property the EditorialModel::fieldtypes::EmFieldType are instanciated to be able to handle datas
        # @see EmComponent::_fields EditorialModel::fieldtypes::EmFieldType
        self._fields = OrderedDict([(name, ftype()) for (name, ftype) in (EmComponent._fields + self.__class__._fields)])
        self.model = model

        for name, value in data.items():
            if name in self._fields:
                self._fields[name].from_string(value)


    ## @brief Access an attribute of an EmComponent
    # This method is overloads the default __getattr__ to search in EmComponents::_fields . If there is an EditorialModel::EmField with a corresponding name in the component
    # it returns its value.
    # @param name str: The attribute name
    # @throw AttributeError if attribute don't exists
    # @see EditorialModel::EmField::value
    def __getattr__(self, name):
        if name != '_fields' and name in self._fields:
            return self._fields[name].value
        else:
            return super(EmComponent, self).__getattribute__(name)

    ## @brief Access an EmComponent attribute
    # This function overload the default __getattribute__ in order to check if the EmComponent was deleted.
    # @param name str: The attribute name
    # @throw EmComponentNotExistError if the component was deleted
    def __getattribute__(self, name):
        if super(EmComponent, self).__getattribute__('deleted'):
            raise EmComponentNotExistError("This " + super(EmComponent, self).__getattribute__('__class__').__name__ + " has been deleted")
        res = super(EmComponent, self).__getattribute(name)
        return res

    ## Set the value of an EmComponent attribute
    # @param name str: The propertie name
    # @param value *: The value
    def __setattr__(self, name, value):
        if name in self.__class__._ro_properties:
            raise TypeError("Propertie '" + name + "' is readonly")

        if name != '_fields' and hasattr(self, '_fields') and name in object.__getattribute__(self, '_fields'):
            self._fields[name].from_python(value)
        else:
            object.__setattr__(self, name, value)
    
    ## @brief Hash function that allows to compare two EmComponent
    # @return EmComponent+ClassName+uid
    def __hash__(self):
        return "EmComponent"+self.__class__.__name__+str(self.uid)

    ## @brief Test if two EmComponent are "equals"
    # @return True or False
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.uid == other.uid

    ## Set all fields
    def populate(self):
        records = []  # TODO

        for record in records:
            for keys in self._fields.keys():
                if keys in record:
                    self._fields[keys].from_string(record[keys])

        super(EmComponent, self).__setattr__('deleted', False)

    ## Check if the EmComponent is valid
    # This function has to check that rank are correct and continuous other checks are made in childs classes
    # @warning Hardcoded minimum rank
    # @warning Rank modified by _fields['rank'].value
    # @return True
    def check(self):
        if self.get_max_rank() > len(self.same_rank_group()):
            #Non continuous ranks
            for i, component in enumerate(self.same_rank_group()):
                component._fields['rank'].value = i + 1
        # No need to sort again here
        return True

    ## @brief Get the maximum rank given an EmComponent child class and a ranked_in filter
    # @return A positive integer or -1 if no components
    def get_max_rank(self):
        components = self.same_rank_group()
        return -1 if len(components) == 0 else components[-1].rank

    ## Return an array of instances that are concerned by the same rank
    # @return An array of instances that are concerned by the same rank
    def same_rank_group(self):
        components = self.model.components(self.__class__)
        ranked_in = self.__class__.ranked_in
        return [ c for c in components if getattr(c, ranked_in) == getattr(self, ranked_in) ]

    ## Set a new rank for this component
    # @note This function assume that ranks are properly set from 1 to x with no gap
    #
    # @warning Hardcoded minimum rank
    # @warning Rank modified by _fields['rank'].value
    #
    # @param new_rank int: The new rank
    #
    # @throw TypeError If bad argument type
    # @throw ValueError if out of bound value
    def set_rank(self, new_rank):
        if not isinstance(new_rank, int):
            raise TypeError("Excepted <class int> but got "+str(type(new_rank)))
        if new_rank <= 0 or new_rank > self.get_max_rank():
            raise ValueError("Invalid new rank : "+str(new_rank))

        mod = new_rank - self.rank #Indicates the "direction" of the "move"

        if mod == 0:
            return True

        limits = [ self.rank + ( 1 if mod > 0 else -1), new_rank ] #The range of modified ranks
        limits.sort()

        for component in [ c for c in self.same_rank_group() if c.rank >= limits[0] and c.rank <= limits[1] ] :
            component._fields['rank'].value = component.rank + ( -1 if mod > 0 else 1 )

        self._fields['rank'].value = new_rank

        self.model.sort_components(self.__class__)

        pass

    ## Modify a rank given an integer modifier
    # @param rank_mod int : can be a negative positive or zero integer
    # @throw TypeError if rank_mod is not an integer
    # @throw ValueError if rank_mod is out of bound
    def modify_rank(self, rank_mod):
        if not isinstance(rank_mod, int):
            raise TypeError("Excepted <class int>, <class str>. But got "+str(type(rank_mod))+", "+str(type(sign)))
        try:
            self.set_rank(self.rank + rank_mod)
        except ValueError:
            raise ValueError("The rank modifier '"+str(rank_mod)+"' is out of bounds")

    ## @brief Return a string representation of the component
    # @return A string representation of the component
    def __repr__(self):
        if self.name is None:
            return "<%s #%s, 'non populated'>" % (type(self).__name__, self.uid)
        else:
            return "<%s #%s, '%s'>" % (type(self).__name__, self.uid, self.name)

    @classmethod
    ## Register a new component in UID table
    #
    # Use the class property table
    # @return A new uid (an integer)
    def new_uid(cls, db_engine):
        if cls.table is None:
            raise NotImplementedError("Abstract method")

        dbe = db_engine

        uidtable = sql.Table('uids', sqlutils.meta(dbe))
        conn = dbe.connect()
        req = uidtable.insert(values={'table': cls.table})
        res = conn.execute(req)

        uid = res.inserted_primary_key[0]
        logger.debug("Registering a new UID '" + str(uid) + "' for '" + cls.table + "' component")

        conn.close()

        return uid


## @brief An exception class to tell that a component don't exist
class EmComponentNotExistError(Exception):
    pass


## @brief Raised on uniq constraint error at creation
# This exception class is dedicated to be raised when create() method is called
# if an EmComponent with this name but different parameters allready exist
class EmComponentExistError(Exception):
    pass


## @brief An exception class to tell that no ranking exist yet for the group of the object
class EmComponentRankingNotExistError(Exception):
    pass
