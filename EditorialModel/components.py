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

    ## Insert a new component
    #
    # This function create and assign a new UID and handle the date_create and date_update values
    # @warning There is a mandatory argument dbconf that indicate wich database configuration to use
    # @param **kwargs : Names arguments representing object properties
    # @return An instance of the created component
    # @throw TypeError if an element of kwargs isn't a valid object propertie or if a mandatory argument is missing
    # @throw RuntimeError if the creation fails at database level
    # @todo Check that every mandatory _fields are given in args
    # @todo Stop using datetime.datetime.utcnow() for date_update and date_create init
    @classmethod
    def create(cls, **kwargs):
        #Checking for invalid arguments
        valid_args = [ name for name,_ in (cls._fields + EmComponent._fields)]

        for argname in kwargs:
            if argname in ['date_update', 'date_create', 'rank', 'uid']:  # Automatic properties
                raise TypeError("Invalid argument : " + argname)
            elif argname not in valid_args:
                raise TypeError("Unexcepted keyword argument '" + argname + "' for " + cls.__name__ + " creation")

        #Check uniq names constraint
        try:
            name = kwargs['name']
            exist = cls(name)
            for kname in kwargs:
                if not (getattr(exist, kname) == kwargs[kname]):
                    raise EmComponentExistError("An " + cls.__name__ + " named " + name + " allready exists with a different " + kname)
            logger.info("Trying to create an " + cls.__name__ + " that allready exist with same attribute. Returning the existing one")
            return exist
        except EmComponentNotExistError:
            pass

        kwargs['uid'] = cls.new_uid()
        kwargs['date_update'] = kwargs['date_create'] = datetime.datetime.utcnow()

        kwargs['rank'] = cls._get_max_rank( kwargs[cls.ranked_in], dbe )+1

        return cls(kwargs['name'], dbconf)

    ## @brief Get the maximum rank given an EmComponent child class and a ranked_in filter
    # @param ranked_in_value mixed: The rank "family"
    # @return -1 if no EmComponent found else return an integer >= 0
    @classmethod
    def _get_max_rank(cls, ranked_in_value):
        pass

    ## Only make a call to the class method
    # @return A positive integer or -1 if no components
    # @see EmComponent::_get_max_rank()
    def get_max_rank(self, ranked_in_value):
        return self.__class__._get_max_rank(ranked_in_value)

    ## Set a new rank for this component
    # @note This function assume that ranks are properly set from 1 to x with no gap
    # @param new_rank int: The new rank
    # @return True if success False if not
    # @throw TypeError If bad argument type
    # @throw ValueError if out of bound value
    def set_rank(self, new_rank):
        if not isinstance(new_rank, int):
            raise TypeError("Excepted <class int> but got "+str(type(new_rank)))
        if new_rank < 0 or new_rank > self.get_max_rank(getattr(self, self.ranked_in)):
            raise ValueError("Invalid new rank : "+str(new_rank))

        mod = new_rank - self.rank #Allow to know the "direction" of the "move"

        if mod == 0: #No modifications
            return True

        limits = [ self.rank + ( 1 if mod > 0 else -1), new_rank ] #The range of modified ranks
        limits.sort()

        dbe = self.db_engine
        conn = dbe.connect()
        table = sqlutils.get_table(self)

        #Selecting the components that will be modified
        req = table.select().where( getattr(table.c, self.ranked_in) == getattr(self, self.ranked_in)).where(table.c.rank >= limits[0]).where(table.c.rank <= limits[1])

        res = conn.execute(req)
        if not res: #Db error... Maybe false is a bit silent for a failuer
            return False

        rows = res.fetchall()

        updated_ranks = [{'b_uid': self.uid, 'b_rank': new_rank}]
        for row in rows:
            updated_ranks.append({'b_uid': row['uid'], 'b_rank': row['rank'] + (-1 if mod > 0 else 1)})
        req = table.update().where(table.c.uid == sql.bindparam('b_uid')).values(rank=sql.bindparam('b_rank'))
        res = conn.execute(req, updated_ranks)
        conn.close()

        if res:
            #Instance rank update
            self._fields['rank'].value = new_rank
        return bool(res)

    ## @brief Modify a rank given a sign and a new_rank
    # - If sign is '=' set the rank to new_rank
    # - If sign is '-' set the rank to cur_rank - new_rank
    # - If sign is '+' set the rank to cur_rank + new_rank
    # @param new_rank int: The new_rank or rank modifier
    # @param sign str: Can be one of '=', '+', '-'
    # @return True if success False if fails
    # @throw TypeError If bad argument type
    # @throw ValueError if out of bound value
    def modify_rank(self,new_rank, sign='='):
        if not isinstance(new_rank, int) or not isinstance(sign, str):
            raise TypeError("Excepted <class int>, <class str>. But got "+str(type(new_rank))+", "+str(type(sign)))

        if sign == '+':
            return self.set_rank(self.rank + new_rank)
        elif sign == '-':
            return self.set_rank(self.rank - new_rank)
        elif sign == '=':
            return self.set_rank(new_rank)
        else:
            raise ValueError("Excepted one of '=', '+', '-' for sign argument, but got "+sign)

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
