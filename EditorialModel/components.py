# -*- coding: utf-8 -*-

## @file components.py
# Defines the EditorialModel::components::EmComponent class and the EditorialModel::components::ComponentNotExistError exception class

import datetime
import logging
from collections import OrderedDict
import hashlib

import EditorialModel.fieldtypes as ftypes
from EditorialModel.exceptions import *
from Lodel.utils.mlstring import MlString

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
 
        self.model = model # AHAH cannot check type without importing Model ? 

        self.uid = uid
        self.check_type('uid', int)
        self.name = name
        self.check_type('name', str)
        self.string = MlString() if string is None else string
        self.check_type('string', MlString)
        self.help_text = MlString() if help_text is None else help_text
        self.check_type('help_text', MlString)
        self.date_update = datetime.datetime.now() if date_update is None else date_update #WARNING timezone !
        self.check_type('date_update', datetime.datetime)
        self.date_create = datetime.datetime.now() if date_create is None else date_create #WARNING timezone !
        self.check_type('date_create', datetime.datetime)

        #Handling specials ranks for component creation
        self.rank = rank
        pass

    @property
    ## @brief Return a dict with attributes name as key and attributes value as value
    # @note Used at creation and deletion to call the migration handler
    def attr_dump(self):
        return {fname: fval for fname, fval in self.__dict__.items() if not (fname.startswith('__') or (fname == 'uid'))}
        
    ## @brief This function has to be called after the instanciation, checks, and init manipulations are done
    # @note Create a new attribute _inited that allow __setattr__ to know if it has or not to call the migration handler
    def init_ended(self):
        self._inited = True

    ## @brief Reimplementation for calling the migration handler to register the change
    def __setattr__(self, attr_name, value):
        inited = '_inited' in self.__dict__
        if inited:
            # if fails raise MigrationHandlerChangeError
            self.model.migration_handler.register_change(self.uid, {attr_name: getattr(self, attr_name) }, {attr_name: value} )
        super(EmComponent, self).__setattr__(attr_name, value)
        if inited:
            self.model.migration_handler.register_model_state(hash(self.model))

    ## Check the type of attribute named var_name
    # @param var_name str : the attribute name
    # @param excepted_type tuple|type : Tuple of type or a type 
    # @throw AttributeError if wrong type detected
    def check_type(self, var_name, excepted_type):
        var = getattr(self, var_name)
        
        if not isinstance(var, excepted_type):
            raise AttributeError("Excepted %s to be an %s but got %s instead" % (var_name, str(excepted_type), str(type(var))) )
        pass

    ## @brief Hash function that allows to compare two EmComponent
    # @return EmComponent+ClassName+uid
    def __hash__(self):
        return int(hashlib.md5(str(self.attr_dump).encode('utf-8')).hexdigest(),16)

    ## @brief Test if two EmComponent are "equals"
    # @return True or False
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.uid == other.uid

    ## Check if the EmComponent is valid
    # This function has to check that rank are correct and continuous other checks are made in childs classes
    # @warning Hardcoded minimum rank
    # @warning Rank modified by _fields['rank'].value
    # @return True
    # @throw EmComponentCheckError if fails
    def check(self):
        if self.get_max_rank() > len(self.same_rank_group()):
            #Non continuous ranks
            for i, component in enumerate(self.same_rank_group()):
                component.rank = i + 1
        # No need to sort again here

    ## @brief Delete predicate. Indicates if a component can be deleted
    # @return True if deletion OK else return False
    def delete_check(self):
        raise NotImplementedError("Virtual method")

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

