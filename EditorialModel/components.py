# -*- coding: utf-8 -*-

## @file components.py
# Defines the EditorialModel::components::EmComponent class and the EditorialModel::components::ComponentNotExistError exception class

import datetime

import logging
import EditorialModel.fieldtypes as ftypes
from Lodel.utils.mlstring import MlString
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

    def __init__(self, model, uid, name, string = None, help_text = None, date_update = None, date_create = None, rank = None):
        if type(self) == EmComponent:
           raise NotImplementedError('Abstract class')
 
        self.model = model
        self.uid = uid
        self.name = name
        self.string = MlString() if string is None else string
        self.help_text = MlString() if help_text is None else help_text
        self.date_update = datetime.datetime.now() if date_update is None else date_update #WARNING timezone !
        self.date_create = datetime.datetime.now() if date_create is None else date_create #WARNING timezone !

        #Handling specials ranks for component creation
        self.rank = rank
        pass

    ## @brief Hash function that allows to compare two EmComponent
    # @return EmComponent+ClassName+uid
    def __hash__(self):
        return "EmComponent"+self.__class__.__name__+str(self.uid)

    ## @brief Test if two EmComponent are "equals"
    # @return True or False
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.uid == other.uid

    ## Check if the EmComponent is valid
    # This function has to check that rank are correct and continuous other checks are made in childs classes
    # @warning Hardcoded minimum rank
    # @warning Rank modified by _fields['rank'].value
    # @return True
    def check(self):
        if self.get_max_rank() > len(self.same_rank_group()):
            #Non continuous ranks
            for i, component in enumerate(self.same_rank_group()):
                component.rank = i + 1
        # No need to sort again here
        return True

    ## @brief Get the maximum rank given an EmComponent child class and a ranked_in filter
    # @return A positive integer or -1 if no components
    def get_max_rank(self):
        components = self.same_rank_group()
        return 1 if len(components) == 0 else components[-1].rank

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
            component.rank = component.rank + ( -1 if mod > 0 else 1 )

        self.rank = new_rank

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
