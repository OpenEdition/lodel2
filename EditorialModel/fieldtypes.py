#-*- coding: utf-8 -*-
import EditorialModel

from Lodel.utils.mlstring import MlString
from sqlalchemy import Column
import sqlalchemy as sql
import datetime
import json
import importlib
import re
import copy

## @file fieldtypes.py
# This file contains classes about SQL column (EmFieldType)
# and their values (EmFieldValue)
# For the moment the code is in quick & dirty version and is
# more like a proof of concept

## @brief Handles SQL types
# This class handles SQL types and their options.
# For the moment it is designed to handles SQLAlchemy types but it
# can be easily ( I hope ) transformed for other purpose
class EmFieldSQLType(object):
    
    ## @brief Dict handling type infos for integers
    _integer = { 'sql' : sql.INTEGER }
    ## @brief Dict handling type infos for big integers
    _bigint = { 'sql' : sql.BIGINT }
    ## @brief Dict handling type infos for small integers
    _smallint = { 'sql' : sql.SMALLINT }
    ## @brief Dict handling type infos for boolean
    _boolean = { 'sql' : sql.BOOLEAN }
    ## @brief Dict handling type infos for floating point numbers
    _float = { 'sql' : sql.FLOAT }
    ## @brief Dict handling type infos for strings
    _varchar = { 'sql' : sql.VARCHAR }
    ## @brief Dict handling type infos for texts
    _text = { 'sql' : sql.TEXT }
    ## @brief Dict handling type infos for time
    _time = { 'sql' : sql.TIME }
    ## @brief Dict handling type infos for date
    _date = { 'sql' : sql.DATE }
    ## @brief Dict handling type infos for datetime
    _datetime = { 'sql' : sql.DATETIME }

    ## @brief Link types names with types informations
    # Names to type associations :
    # - Integer : ''int'', ''integer''
    # - Big integer : ''bigint''
    # - Small integer : ''smallint''
    # - Boolean value : ''bool'', ''boolean''
    # - Floating point number : ''float''
    # - String : ''char'', ''varchar''
    # - Text : ''text''
    # - Time : ''time''
    # - Date : ''date''
    # - Date & time : ''datetime''
    _names = {
        'int' : _integer,
        'integer' : _integer,
        'bigint' : _bigint,
        'smallint' : _smallint,
        'boolean' : _boolean,
        'bool' : _boolean,
        'float' : _float,
        'char' : _varchar,
        'varchar' : _varchar,
        'text' : _text,
        'time' : _time,
        'date' : _date,
        'datetime' : _datetime,
    }

    @classmethod
    ## Get an sql type (actually sqlalchemy type)
    # @param str: Type name
    # @param **kwargs : Please refer to sqlalchemy doc to see available options for each type
    # @return An sqlalchemy type
    # @throw TypeError if name not str or size not int nor None
    # @throw ValueError if name is not a valid type name
    def sqlType(cl, name, **kwargs):
        if not isinstance(name, str):
            raise TypeError("Expect <class str>, <class int>|None but got : "+str(type(name))+" "+str(type(size)))
        name = name.lower()
        if name not in cl._names:
            raise ValueError("Unknown type '"+name+"'")
        if len(kwargs) == 0:
            return cl._names[name]['sql']
        return cl._names[name]['sql'](**kwargs)
        
        

class EmFieldType(object):
 
    ## Stores options and default value for EmFieldType
    # options list : 
    # - type (str|None) : if None will make an 'abstract' fieldtype (with no value assignement possible)
    # - size (int) : The size for this type
    # - nullable (bool) : tell whether or not a fieldType accept NULL value
    # - default (mixed) : The default value for a FieldType
    # - primarykey (bool) : If true the fieldType represent a PK
    # - autoincrement (bool) : If true the fieldType will be autoincremented
    # - index (bool) : If true the columns will be indexed in Db
    # - name (str) : FieldType name
    # - doc (str) : FieldType documentation
    # - onupdate (callable) : A callback to call on_update
    # - valueobject (EmFieldValue or childs) : An object that represent values for this fieldType
    # - type_* (mixed) : Use to construct an options dictinnary for a type (exemple : type_length => nnewColumn(lenght= [type_lenght VALUE] ))
    _opt = {
        'name' : None,
        'type' : None,
        'size': None,
        'nullable': True,
        'default' : None,
        'primarykey': False,
        'autoincrement' : False,
        'uniq' : False,
        'index': False,
        'doc' : None,
        'onupdate': None,
        'valueobject': None,
    }
    

    ## Instanciate an EmFieldType
    # For arguments see @ref EmFieldType::_opt
    def __init__(self, **kwargs):
        self._init(kwargs)
        self.type_options = dict()
        #Stores all col_* arguments into the self.col_options dictionnary
        args = kwargs.copy()
        for optname in args:
            type_opt = re.sub(r'^type_', '', optname)
            if type_opt != optname:
                self.type_options[type_opt] = args[optname]
                del kwargs[optname]
                
        #Check if the others arguments are valids
        if len(set(kwargs.keys()) - set(self.__class__._opt.keys())) > 0:
            badargs = ""
            for bad in set(kwargs.keys()) - set(self.__class__._opt.keys()):
                badargs += " "+bad
            raise TypeError("Unexpected arguments : "+badargs)

        #Stores other arguments as instance attribute
        for opt_name in self.__class__._opt:
            setattr(self, opt_name, (kwargs[opt_name] if opt_name in kwargs else self.__class__._opt[opt_name]))

        #Checking type's options validity
        if self.type != None:
            try:
                EmFieldSQLType.sqlType(self.type, **self.type_options)
            except TypeError as e:
                raise e
                #raise TypeError("Bad type option in on of those arguments : "+str(["type_"+opt for opt in self.type_options]))

        #Default value for name
        if self.name == None:
            if self.__class__ == EmFieldType:
                self.name = 'generic'
            else:
                self.name = self.__class__.__name__
        # Default value for doc
        if self.doc == None:
            if self.__class__ == EmFieldType:
                self.doc = 'Abstract generic EmFieldType'
            else:
                self.doc = self.__class__.__name__
        pass

    @property
    ## A predicate that indicate wether or not an EmFieldType is ''abstract''
    def abstract(self):
        return (self.type == None)

    ## MUST been called first in each constructor
    # @todo this solution is not good (look at the __init__ for EmFieldType childs)
    def _init(self, kwargs):
        try:
            self.args_copy
        except AttributeError:
            self.args_copy = kwargs.copy()
        pass
    
    ## Return a copy of the current EmFieldType
    def copy(self):
        args = self.args_copy.copy()
        return self.__class__(**args)

    def dump_opt(self):
        return json.dumps(self.args_copy)

    @staticmethod
    ## Return an instance from a classname and options from dump_opt
    # @param classname str: The EmFieldType class name
    # @param json_opt str: getted from dump_opt
    def restore(colname, classname, json_opt):
        fieldTypeClass = getattr(EditorialModel.fieldtypes, classname)
        init_opt = json.loads(json_opt)
        init_opt['name'] = colname
        return fieldTypeClass(**init_opt)

    ## Return a SQL column (actually an sqlAlchemy column)
    def sqlCol(self):
        return sql.Column(
            name = self.name,
            type_ = EmFieldSQLType.sqlType(self.type, **self.type_options),
            autoincrement = self.autoincrement,
            nullable = self.nullable,
            default = self.default,
            doc = self.doc,
            index = self.index,
            primary_key = self.primarykey,
            onupdate = self.onupdate,
        )

    ## Return a value object 'driven' by this EmFieldType
    # @param name str: The column name associated with the value
    # @param *init_val mixed: If given this will be the initialisation value
    # @return a EmFieldValue instance
    # @todo better default value (and bad values) handling
    def valueObject(self, name, *init_val):
        if self.valueobject == None:
            return EmFieldValue(name, self, *init_val)
        return self.valueobject(name, self, *init_val)

    ## Cast to the correct value
    # @param v mixed: The value to cast
    # @return A gently casted value
    # @throw ValueError if v is innapropriate
    # @throw NotImplementedError if self is an abstract EmFieldType
    def to_value(self, v):
        if self.type == None:
            raise NotImplementedError("This EmFieldType is abstract")
        if v == None and not self.nullable:
            raise TypeError("Field not nullable")
        return v
    ## to_value alias
    def from_string(self, value): return self.to_value(value)

    ## Return a gently sql forged value
    # @return A gently sql forged value
    # @warning It assume that value is corret and comes from an EmFieldValue object
    def to_sql(self, value):
        if self.abstract:
            raise NotImplementedError("This EmFieldType is abstract")
        return value

    @classmethod
    ## Function designed to be called by child class to enforce a type
    # @param args dict: The kwargs argument of __init__
    # @param typename str: The typename to enforce
    # @return The new kwargs to be used
    # @throw TypeError if type is present is args
    def _setType(cl, args, typename):
        return cl._argEnforce(args, 'type', typename, True)

    @classmethod
    ## Function designed to be called by child's constructo to enforce an argument
    # @param args dict: The constructor's kwargs 
    # @param argname str: The name of the argument to enforce
    # @param argval mixed: The value we want to enforce
    # @param Return a new kwargs
    # @throw TypeError if type is present is args and exception argument is True
    def _argEnforce(cl, args, argname, argval, exception=True):
        if exception and argname in args:
            raise TypeError("Invalid argument '"+argname+"' for "+cl.__class__.__name__+" __init__")
        args[argname] = argval
        return args

    @classmethod
    ## Function designed to be called by child's constructor to set a default value
    # @param args dict: The constructor's kwargs
    # @param argname str: The name of the argument with default value
    # @param argval mixed : The default value
    # @return a new kwargs dict
    def _argDefault(cl, args, argname, argval):
        if argname not in args:
            args[argname] = argval
        return args


class EmFieldValue(object):

    ## Instanciate a EmFieldValue
    # @param name str: The column name associated with this value
    # @param fieldtype EmFieldType: The EmFieldType defining the value
    # @param *value *list: This argument allow to pass a value to set (even None) and to detect if no value given to set to EmFieldType's default value
    # @throw TypeError if more than 2 arguments given
    # @throw TypeError if fieldtype is not an EmFieldType
    # @throw TypeError if fieldtype is an abstract EmFieldType
    def __init__(self, name, fieldtype, *value):
        if not isinstance(fieldtype, EmFieldType):
            raise TypeError("Excepted <class EmFieldType> for 'fieldtype' argument. But got : "+str(type(fieldtype)))
        if fieldtype.abstract:
            raise TypeError("The fieldtype given in argument is abstract.")

        # This copy ensure that the fieldtype will not change during the value lifecycle
        super(EmFieldValue,self).__setattr__('fieldtype', fieldtype.copy())

        if len(value) > 1:
            raise TypeError("Accept only 2 positionnal parameters. "+str(len(value)+1)+" given.")
        elif len(value) == 1:
            self.value = value[0]
        else:
            self.value = fieldtype.default

        #use this to set value in the constructor
        setv = super(EmFieldValue, self).__setattr__
        # This copy makes column attributes accessible easily
        for attrname in self.fieldtype.__dict__:
            setv(attrname, getattr(self.fieldtype, attrname))
        
        # Assign some EmFieldType methods to the value
        setv('from_python', self.fieldtype.to_value)
        setv('from_string', self.fieldtype.to_value)
        setv('sqlCol', self.fieldtype.sqlCol)
        pass

    ## @fn from_python
    # Alias for EmFieldType::to_value()

    ## @fn from_string
    # Alias for EmFieldType::to_value()

    ## @fn sqlCol
    # Alias for EmFieldType::sqlCol()

    ## The only writable attribute of EmFieldValue is the value
    # @param name str: Have to be value
    # @param value mixed: The value to set
    # @throw AtrributeError if another attribute than value is to be set
    # @throw ValueError if self.to_value raises it
    # @see EmFieldType::to_value()
    def __setattr__(self, name, value):
        if name != "value":
            raise AttributeError("EmFieldValue has only the value property settable")
        super(EmFieldValue,self).__setattr__('value', self.fieldtype.to_value(value))
    

    ##
    # @warning When getting the fieldtype you actually get a copy of it to prevent any modifications !
    def __getattr__(self, name):
        if name == 'fieldtype':
            return self.fieldtype.copy()
        return super(EmFieldValue, self).__getattribute__(name)

        
    ## @brief Return an sql valid value
    #
    # Can be used to convert any value (giving one positionnal argument) or to return the current value
    # @param *value list: If a positionnal argument is given return it and not the instance value 
    # @return A value suitable for sql
    def to_sql(self, *value):
        if len(value) > 1:
            raise TypeError("Excepted 0 or 1 positional argument but got "+str(len(value)))
        elif len(value) == 1:
            return self.fieldtype.to_sql(value[0])
        return self.fieldtype.to_sql(self.value)

## @brief Designed to handle values that has common arithmetic operations
class EmFieldValue_int(EmFieldValue):
       
    def __int__(self):
        return self.value

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __mul__(self, other):
        return self.value * other

    def __div__(self, other):
        return self.value / other

    def __mod__(self, other):
        return self.value % other

    def __iadd__(self, other):
        self.value = int(self.value + other)
        return self

    def __isub__(self, other):
        self.value = int(self.value - other)
        return self

    def __imul__(self, other):
        self.value = int(self.value * other)
        return self

    def __idiv__(self, other):
        self.value = int(self.value / other)
        return self
        
class EmField_integer(EmFieldType):
    def __init__(self, **kwargs):
        self._init(kwargs)
        #Default name
        kwargs = self.__class__._argDefault(kwargs, 'name', 'integer')
        #Type enforcing
        kwargs = self.__class__._setType(kwargs, 'int')
        super(EmField_integer, self).__init__(**kwargs)
        self.valueobject = EmFieldValue_int
        pass
    ##
    # @todo catch cast error ?
    def to_sql(self, value):
        return value

    def to_value(self,value):
        if value == None:
            return super(EmField_integer, self).to_value(value)
        return int(value)


class EmField_boolean(EmFieldType):
    def __init__(self, **kwargs):
        self._init(kwargs)
        #Default name
        kwargs = self.__class__._argDefault(kwargs, 'name', 'boolean')
        #Type enforcing
        kwargs = self.__class__._setType(kwargs, 'boolean')
        super(EmField_boolean, self).__init__(**kwargs)
        pass
    def to_sql(self, value):
        return 1 if super(EmField_boolean, self).to_sql(value) else 0
    def to_value(self, value):
        if value == None:
            return super(EmField_boolean, self).to_value(value)
        self.value = bool(value)

class EmField_char(EmFieldType):
    default_length = 76
    def __init__(self, **kwargs):
        self._init(kwargs)
        kwargs = self.__class__._argDefault(kwargs, 'type_length', self.__class__.default_length)
        kwargs = self.__class__._argDefault(kwargs, 'name', 'char')
        #Type enforcing
        kwargs = self.__class__._setType(kwargs, 'varchar')
        super(EmField_char, self).__init__(**kwargs)
    def to_sql(self, value):
        return str(value)
##
# @todo rename to EmField_datetime
# @todo timezones support
class EmField_date(EmFieldType):
    def __init__(self, **kwargs):
        self._init(kwargs)
        kwargs = self.__class__._argDefault(kwargs, 'name', 'date')
        #Type enforcing
        kwargs = self.__class__._setType(kwargs, 'datetime')
        super(EmField_date, self).__init__(**kwargs)

    def to_sql(self, value):
        return value #thanks to sqlalchemy

    def to_value(self, value):
        if value == None:
            return super(EmField_date, self).to_value(value)
        if isinstance(value, int):
            #assume its a timestamp
            return datetime.fromtimestamp(value)
        if isinstance(value, datetime.datetime):
            return value

class EmField_mlstring(EmField_char):
    
    def __init__(self, **kwargs):
        self._init(kwargs)
        kwargs = self.__class__._argDefault(kwargs, 'name', 'mlstr')
        super(EmField_mlstring, self).__init__(**kwargs)

    def to_sql(self, value):
        return value.__str__()

    def to_value(self, value):
        if value == None:
            return super(EmField_mlstring, self).to_value(value)
        if isinstance(value, str):
            return MlString.load(value)
        elif isinstance(value, MlString):
            return value
        raise TypeError("<class str> or <class MlString> excepted. But got "+str(type(value)))

class EmField_uid(EmField_integer):
    def __init__(self, **kwargs):
        self._init(kwargs)
        kwargs = self.__class__._argEnforce(kwargs, 'primarykey', True)
        super(EmField_uid, self).__init__(**kwargs)
        pass

