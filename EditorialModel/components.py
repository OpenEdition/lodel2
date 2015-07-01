# -*- coding: utf-8 -*-

## @file components.py
# Defines the EditorialModel::components::EmComponent class and the EditorialModel::components::ComponentNotExistError exception class

import datetime

import logging
import sqlalchemy as sql
from Database import sqlutils
import EditorialModel.fieldtypes as ftypes
from collections import OrderedDict

logger = logging.getLogger('Lodel2.EditorialModel')


## This class is the mother class of all editorial model objects
#
# It gather all the properties and mechanism that are common to every editorial model objects
# @see EditorialModel::classes::EmClass, EditorialModel::types::EmType, EditorialModel::fieldgroups::EmFieldGroup, EditorialModel::fields::EmField
# @pure
class EmComponent(object):

    ## The name of the engine configuration
    # @todo Not a good idea to store it here
    dbconf = 'default'
    ## The table in wich we store data for this object
    # None for EmComponent
    table = None
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
    def __init__(self, id_or_name):
        if type(self) == EmComponent:
            raise NotImplementedError('Abstract class')

        ## @brief An OrderedDict storing fields name and values
        # Values are handled by EditorialModel::fieldtypes::EmFieldType
        # @warning \ref _fields instance property is not the same than EmComponent::_fields class property. In the instance property the EditorialModel::fieldtypes::EmFieldType are instanciated to be able to handle datas
        # @see EmComponent::_fields EditorialModel::fieldtypes::EmFieldType
        self._fields = OrderedDict([(name, ftype()) for (name, ftype) in (EmComponent._fields + self.__class__._fields)])

        # populate
        if isinstance(id_or_name, int):
            self._fields['uid'].value = id_or_name  # read only propertie set
        elif isinstance(id_or_name, str):
            self.name = id_or_name
        else:
            raise TypeError('Bad argument: expecting <int> or <str> but got : ' + str(type(id_or_name)))
        self.table = self.__class__.table
        self.populate()

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

    ## Lookup in the database properties of the object to populate the properties
    # @throw EmComponentNotExistError if the instance is not anymore stored in database
    def populate(self):
        records = self._populate_db()  # Db query

        for record in records:
            for keys in self._fields.keys():
                if keys in record:
                    self._fields[keys].from_string(record[keys])

        super(EmComponent, self).__setattr__('deleted', False)

    @classmethod
    ## Shortcut that return the sqlAlchemy engine
    def db_engine(cls):
        return sqlutils.getEngine(cls.dbconf)

    ## Do the query on the database for EmComponent::populate()
    # @throw EmComponentNotExistError if the instance is not anymore stored in database
    def _populate_db(self):
        dbe = self.__class__.db_engine()
        component = sql.Table(self.table, sqlutils.meta(dbe))
        req = sql.sql.select([component])

        if self.uid is None:
            req = req.where(component.c.name == self.name)
        else:
            req = req.where(component.c.uid == self.uid)
        conn = dbe.connect()
        res = conn.execute(req)

        res = res.fetchall()
        conn.close()

        if not res or len(res) == 0:
            raise EmComponentNotExistError("No " + self.__class__.__name__ + " found with " + ('name ' + self.name if self.uid is None else 'uid ' + str(self.uid)))

        return res

    ## Insert a new component in the database
    #
    # This function create and assign a new UID and handle the date_create and date_update values
    #
    # @param **kwargs : Names arguments representing object properties
    # @return An instance of the created component
    # @throw TypeError if an element of kwargs isn't a valid object propertie or if a mandatory argument is missing
    #
    # @todo Check that the query didn't failed
    # @todo Check that every mandatory _fields are given in args
    # @todo Put a real rank at creation
    # @todo Stop using datetime.datetime.utcnow() for date_update and date_create init
    @classmethod
    def create(cls, **kwargs):
        for argname in kwargs:
            if argname in ['date_update', 'date_create', 'rank', 'uid']:  # Automatic properties
                raise TypeError("Invalid argument : " + argname)

        #TODO check that every mandatory _fields are here like below for example
        #for name in cls._fields:
        #    if cls._fields[name].notNull and cls._fields[name].default == None:
        #        raise TypeError("Missing argument : "+name)

        kwargs['uid'] = cls.new_uid()
        kwargs['date_update'] = kwargs['date_create'] = datetime.datetime.utcnow()

        dbe = cls.db_engine()
        conn = dbe.connect()

        #kwargs['rank'] = cls.get_max_rank(kwargs[cls.ranked_in]) + 1 #Warning !!!
        kwargs['rank'] = -1

        table = sql.Table(cls.table, sqlutils.meta(dbe))
        req = table.insert(kwargs)
        conn.execute(req)  # Check ?
        conn.close()
        return cls(kwargs['name'])  # Maybe no need to check res because this would fail if the query failed

    ## Write the representation of the component in the database
    # @return bool
    # @todo stop using datetime.datetime.utcnow() for date_update update
    def save(self):
        values = {}
        for name, field in self._fields.items():
            values[name] = field.to_sql()

        # Don't allow creation date overwritting
        #if 'date_create' in values:
            #del values['date_create']
            #logger.warning("date_create supplied for save, but overwritting of date_create not allowed, the date will not be changed")

        values['date_update'] = datetime.datetime.utcnow()

        self._save_db(values)

    ## Do the query in the datbase for EmComponent::save()
    # @param values dict: A dictionnary of the values to insert
    # @throw RunTimeError if it was unable to do the Db update
    def _save_db(self, values):
        """ Do the query on the db """
        dbe = self.__class__.db_engine()
        component = sql.Table(self.table, sqlutils.meta(dbe))
        req = sql.update(component, values=values).where(component.c.uid == self.uid)

        conn = dbe.connect()
        res = conn.execute(req)
        conn.close()
        if not res:
            raise RuntimeError("Unable to save the component in the database")

    ## Delete this component data in the database
    # @return bool : True if deleted False if deletion aborded
    # @todo Use something like __del__ instead (or call it at the end)
    # @throw RunTimeError if it was unable to do the deletion
    def delete(self):
        #<SQL>
        dbe = self.__class__.db_engine()
        component = sql.Table(self.table, sqlutils.meta(dbe))
        req = component.delete().where(component.c.uid == self.uid)
        conn = dbe.connect()
        res = conn.execute(req)
        conn.close()
        if not res:
            raise RuntimeError("Unable to delete the component in the database")

        super(EmComponent, self).__setattr__('deleted', True)
        #</SQL>
        return True

    ## get_max_rank
    # Retourne le rank le plus élevé pour le groupe de component au quel apartient l'objet actuelle
    #return int
    @classmethod
    def get_max_rank(cls, ranked_in_value):
        dbe = cls.getDbE()
        component = sql.Table(cls.table, sqlutils.meta(dbe))
        req = sql.sql.select([component.c.rank]).where(getattr(component.c, cls.ranked_in) == ranked_in_value).order_by(component.c.rank.desc())
        c = dbe.connect()
        res = c.execute(req)
        res = res.fetchone()
        c.close()
        if(res != None):
            return res['rank']
        else:
            return -1
            #logger.error("Bad argument")
            #raise EmComponentRankingNotExistError('The ranking of the component named : ' + self.name + 'is empty')

    ## modify_rank
    #
    # Permet de changer le rank d'un component, soit en lui donnant un rank précis, soit en augmentant ou reduisant sont rank actuelle d'une valleur donné.
    #
    # @param new_rank int: le rank ou modificateur de rank
    # @param sign str: Un charactère qui peut être : '=' pour afecter un rank, '+' pour ajouter le modificateur de rank ou '-' pour soustraire le modificateur de rank.
    #
    # @return bool: True en cas de réussite False en cas d'echec.
    # @throw TypeError if an argument isn't from the expected type
    # @thrown ValueError if an argument as a wrong value but is of the good type
    def modify_rank(self, new_rank, sign='='):
        
        if isinstance(new_rank, int):
            if (new_rank >= 0):
                dbe = self.__class__.db_engine()
                component = sql.Table(self.table, sqlutils.meta(dbe))
                req = sql.sql.select([component.c.uid, component.c.rank])

                if (type(sign) is not str):
                    logger.error("Bad argument")
                    raise TypeError('Excepted a string (\'=\' or \'+\' or \'-\') not a ' + str(type(sign)))

                if (sign == '='):
                    req = sql.sql.select([component.c.uid, component.c.rank])
                    req = req.where((getattr(component.c, self.ranked_in) == getattr(self, self.ranked_in)) & (component.c.rank == new_rank))
                    conn = dbe.connect()
                    res = conn.execute(req)
                    res = res.fetchone()
                    conn.close()

                    if (res is not None):
                        req = sql.sql.select([component.c.uid, component.c.rank])
                        if(new_rank < self.rank):
                            req = req.where((getattr(component.c, self.ranked_in) == getattr(self, self.ranked_in)) & (component.c.rank >= new_rank) & (component.c.rank < self.rank))
                        else:
                            req = req.where((getattr(component.c, self.ranked_in) == getattr(self, self.ranked_in)) & (component.c.rank <= new_rank) & (component.c.rank > self.rank))

                        conn = dbe.connect()
                        res = conn.execute(req)
                        res = res.fetchall()

                        vals = list()
                        vals.append({'id': self.uid, 'rank': new_rank})

                        for row in res:
                            if(new_rank < self.rank):
                                vals.append({'id': row.uid, 'rank': row.rank + 1})
                            else:
                                vals.append({'id': row.uid, 'rank': row.rank - 1})

                        req = component.update().where(component.c.uid == sql.bindparam('id')).values(rank=sql.bindparam('rank'))
                        conn.execute(req, vals)
                        conn.close()

                        self._fields['rank'].value = new_rank

                    else:
                        logger.error("Bad argument")

                        raise ValueError('new_rank to big, new_rank - 1 doesn\'t exist. new_rank = '+str((new_rank)))
                elif(sign == '+' and self.rank + new_rank <= self.__class__.get_max_rank(getattr(self, self.__class__.ranked_in))):
                    req = sql.sql.select([component.c.uid, component.c.rank])
                    req = req.where((getattr(component.c, self.ranked_in) == getattr(self, self.ranked_in)) & (component.c.rank == self.rank + new_rank))
                    conn = dbe.connect()
                    res = conn.execute(req)
                    res = res.fetchone()
                    conn.close()

                    if (res is not None):
                        if (new_rank != 0):
                            req = sql.sql.select([component.c.uid, component.c.rank])
                            req = req.where((getattr(component.c, self.ranked_in) == getattr(self, self.ranked_in)) & (component.c.rank <= self.rank + new_rank) & (component.c.rank > self.rank))

                            conn = dbe.connect()
                            res = conn.execute(req)
                            res = res.fetchall()

                            vals = list()
                            vals.append({'id': self.uid, 'rank': self.rank + new_rank})

                            for row in res:
                                vals.append({'id': row.uid, 'rank': row.rank - 1})

                            req = component.update().where(component.c.uid == sql.bindparam('id')).values(rank=sql.bindparam('rank'))
                            conn.execute(req, vals)
                            conn.close()

                            self._fields['rank'] += new_rank
                        else:
                            logger.error("Bad argument")
                            raise ValueError('Excepted a positive int not a null. new_rank = ' + str((new_rank)))
                    else:
                        logger.error("Bad argument")
                        raise ValueError('new_rank to big, rank + new rank doesn\'t exist. new_rank = ' + str((new_rank)))
                elif (sign == '-' and self.rank - new_rank >= 0):
                    if ((self.rank + new_rank) > 0):
                        if (new_rank != 0):
                            req = sql.sql.select([component.c.uid, component.c.rank])
                            req = req.where((getattr(component.c, self.ranked_in) == getattr(self, self.ranked_in)) & (component.c.rank >= self.rank - new_rank) & (component.c.rank < self.rank))

                            conn = dbe.connect()
                            res = conn.execute(req)
                            res = res.fetchall()

                            vals = list()
                            vals.append({'id': self.uid, 'rank': self.rank - new_rank})

                            for row in res:
                                vals.append({'id': row.uid, 'rank': row.rank + 1})

                            req = component.update().where(component.c.uid == sql.bindparam('id')).values(rank=sql.bindparam('rank'))
                            conn.execute(req, vals)
                            conn.close()

                            self._fields['rank'] -= new_rank
                        else:
                            logger.error("Bad argument")
                            raise ValueError('Excepted a positive int not a null. new_rank = ' + str((new_rank)))
                    else:
                        logger.error("Bad argument")
                        raise ValueError('new_rank to big, rank - new rank is negative. new_rank = ' + str((new_rank)))
                else:
                    logger.error("Bad argument")
                    raise ValueError('Excepted a string (\'=\' or \'+\' or \'-\') not a ' + str((sign)))

            else:
                logger.error("Bad argument")
                raise ValueError('Excepted a positive int not a negative. new_rank = ' + str((new_rank)))
        else:
            logger.error("Bad argument")
            raise TypeError('Excepted a int not a ' + str(type(new_rank)))

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
    def new_uid(cls):
        if cls.table is None:
            raise NotImplementedError("Abstract method")

        dbe = cls.db_engine()

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


## @brief An exception class to tell that no ranking exist yet for the group of the object
class EmComponentRankingNotExistError(Exception):
    pass
