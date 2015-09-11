#-*- coding: utf-8 -*-

from django.db import models
import re
import datetime
import json
import importlib
import copy
import EditorialModel
from Lodel.utils.mlstring import MlString


## @brief Characterise fields for LeObject and EmComponent
# This class handles values rules for LeObject and EmComponents.
#
# It allows to EmFieldValue classes family to have rules to cast, validate and save values.
#
# There is exposed methods that allows LeObject and EmType to run a save sequence. This methods are :
# - EmFieldType.to_value() That cast a value to an EmFieldType internal storage
# - EmFieldType.is_valid() That indicates wether or not a value is valid
# - EmFieldType.pre_save() That returns weighted SQL request that must be run before any value save @ref EditorialModel::types::EmType.save_values()
# - EmFieldType.to_sql() That returns a value that can be inserted in database.
# - EmFieldType.post_save() That returns weighted SQL request that must be run after any value save @ref EditorialModel::types::EmType.save_values()
#
class EmFieldType(object):

    ## Stores options and default value for EmFieldType
    # options list :
    # - type (str|None) : if None will make an 'abstract' fieldtype (with no value assignement possible)
    # - nullable (bool) : tell whether or not a fieldType accept NULL value
    # - default (mixed) : The default value for a FieldType
    # - primarykey (bool) : If true the fieldType represent a PK
    # - autoincrement (bool) : If true the fieldType will be autoincremented
    # - index (bool) : If true the columns will be indexed in Db
    # - name (str) : FieldType name
    # - doc (str) : FieldType documentation
    # - onupdate (callable) : A callback to call on_update
    # - valueobject (EmFieldValue or childs) : An object that represent values for this fieldType
    # - type_* (mixed) : Use to construct an options dictinnary for a type (exemple : type_length => nnewColumn(lenght= [type_lenght VALUE] )) @ref EmFieldSQLType
    # - validators (list) : List of validator functions to use
    _opt = {
        'name': None,
        'type': None,
        'nullable': True,
        'default': None,
        'primarykey': False,
        'autoincrement': False,
        'uniq': False,
        'index': False,
        'doc': None,
        'onupdate': None,
        'valueobject': None,
        'validators': None
    }

    ## Instanciate an EmFieldType
    # For arguments see @ref EmFieldType::_opt
    # @see EmFieldType::_opt
    def __init__(self, **kwargs):
        self.__init(kwargs)
        self.type_options = dict()

        # stores all col_* arguments into the self.type_options dictionary
        args = kwargs.copy()
        for optname in args:
            type_opt = re.sub(r'^type_', '', optname)
            if type_opt != optname:
                self.type_options[type_opt] = args[optname]
                del kwargs[optname]

        # checks if the other arguments are valid
        if len(set(kwargs.keys()) - set(self.__class__._opt.keys())) > 0:
            badargs = ""
            for bad in set(kwargs.keys()) - set(self.__class__._opt.keys()):
                badargs += " " + bad
            raise TypeError("Unexpected arguments : %s" % badargs)

        # stores other arguments as instance attribute
        for opt_name in self.__class__._opt:
            setattr(self, opt_name, (kwargs[opt_name] if opt_name in kwargs else self.__class__._opt[opt_name]))

        # checks type's options valididty
        if self.type != None:
            try:
                EmFieldSQLType.sqlType(self.type, **self.type_options)
            except TypeError as e:
                raise e

        # Default value for name
        if self.name == None:
            if  self.__class__ == EmFieldType:
                self.name = 'generic'
            else:
                self.name = self.__class__.__name__

        # Default value for doc
        if self.doc == None:
            if self.__class__ == EmFieldType:
                self.doc = 'Abstract generic EmFieldType'
            else:
                self.doc = self.__class__.__name__

    ## MUST be called first in each constructor
    # @todo this solution is not good (look at the __init__ for EmFieldType childs)
    def __init(self, kwargs):
        try:
            self.args_copy
        except AttributeError:
            self.args_copy = kwargs.copy()

    @property
    ## A predicate that indicates whether or not an EmFieldType is "abstract"
    def is_abstract(self):
        return (self.type == None)

    ## Returns a copy of the current EmFieldType
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
        field_type_class = getattr(EditorialModel.fieldtypes, classname)
        init_opt = json.loads(json_opt)
        init_opt['name'] = colname
        return field_type_class(**init_opt)

    ## Return a value object 'driven' by this EmFieldType
    # @param name str: The column name associated with the value
    # @param *init_val mixed: If given this will be the initialisation value
    # @return a EmFieldValue instance
    # @todo better default value (and bad values) handling
    def valueObject(self, name, *init_val):
        if self.valueObject == None:
            return EmFieldValue(name, self, *init_val)
        return self.valueObject(name, self, *init_val)

    ## Cast to the correct value
    # @param v mixed : the value to cast
    # @return A gently casted value
    # @throw ValueError if v is innapropriate
    # @throw NotImplementedError if self is an abstract EmFieldType
    def to_value(self, v):
        if self.type == None:
            raise NotImplemented("This EmFieldType is abstract")
        if v == None and not self.nullable:
            raise TypeError("Field not nullable")
        return v

    ## to_value alias
    # @param value mixed : the value to cast
    # @return A casted value
    def from_string(self, value):
        return self.to_value(value)

    ## Returns a gently sql forged value
    # @return A sql forged value
    # @warning It assumes that the value is correct and comes from an EmFieldValue object
    def to_sql(self, value):
        if self.is_abstract:
            raise NotImplementedError("This EmFieldType is abstract")
        return True

    ## Returns whether or not a value is valid for this EmFieldType
    # @note This function always returns True and is here for being overloaded  by child objects
    # @return A boolean, True if valid else False
    def is_valid(self, value):
        if self.is_abstract:
            raise NotImplementedError("This EmFieldType is abstract")
        return True

    ## Pre-save actions
    def pre_save(self):
        if self.is_abstract:
            raise NotImplementedError("This EmFieldType is abstract")
        return []

    ## Post-save actions
    def post_save(self):
        if self.is_abstract:
            raise NotImplementedError("This EmFieldType is abstract")
        return []

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

    ## Instanciates a EmFieldValue
    # @param name str : The column name associated with this value
    # @param fieldtype EmFieldType: The EmFieldType defining the value
    # @param *value *list: This argument allow to pass a value to set (even None) and to detect if no value given to set to EmFieldType's default value
    # @throw TypeError if more than 2 arguments given
    # @throw TypeError if fieldtype is not an EmFieldType
    # @throw TypeError if fieldtype is an abstract EmFieldType
    def __init__(self, name, fieldtype, *value):
        if not isinstance(fieldtype, EmFieldType):
            raise TypeError("Expected <class EmFieldType> for 'fieldtype' argument, but got : %s instead" % str(type(fieldtype)))
        if fieldtype.is_abstract:
            raise TypeError("The given fieldtype in argument is abstract.")

        # This copy ensures that the fieldtype will not change during the value lifecycle
        super(EmFieldValue, self).__setattr__('fieldtype', fieldtype.copy())

        if len(value) > 1:
            raise TypeError("Accept only 2 positionnal parameters. %s given." % str(len(value)+1))
        elif len(value) == 1:
            self.value = value[0]
        else:
            self.value = fieldtype.default

        # Use this to set value in the constructor
        setv = super(EmFieldValue, self).__setattr__
        # This copy makes column attributes accessible easily
        for attrname in self.fieldtype.__dict__:
            setv(attrname, getattr(self.fieldtype, attrname))

        # Assign some EmFieldType methods to the value
        setv('from_python', self.fieldtype.to_value)
        setv('from_string', self.fieldtype.to_value)
        #setv('sqlCol', self.fieldtype.sqlCol)

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

    ## @brief Return a valid SQL value
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

class EmFieldSQLType(object):
    _integer = {'sql': models.IntegerField}
    _bigint = {'sql': models.BigIntegerField}
    _smallint = {'sql': models.SmallIntegerField}
    _boolean = {'sql': models.BooleanField}
    _nullableboolean = {'sql': models.NullBooleanField}
    _float = {'sql': models.FloatField}
    _varchar = {'sql': models.CharField}
    _text = {'sql': models.TextField}
    _time = {'sql': models.TimeField}
    _date = {'sql': models.DateField}
    _datetime = {'sql': models.DateTimeField}

    _names = {
        'int': _integer,
        'integer': _integer,
        'bigint': _bigint,
        'smallint': _smallint,
        'boolean': _boolean,
        'bool': _boolean,
        'float': _float,
        'char': _varchar,
        'varchar': _varchar,
        'text': _text,
        'time': _time,
        'date': _date,
        'datetime': _datetime,
    }

    @classmethod
    def sqlType(cls, name, **kwargs):
        if not isinstance(name, str):
            raise TypeError("Expect <class str>, <class int>|None but got : %s %s" % (str(type(name)), str(type(size))))
        name = name.lower()
        if name not in cls._names:
            raise ValueError("Unknown type '%s'" % name)

        if name in ['boolean','bool'] and kwargs['nullable'] in [1,'true']:
            sqlclass = _nullableboolean
        else:
            sqlclass = cls._names[name]

        if len(kwargs) == 0:
            return sqlclass['sql']

        return sqlclass['sql'](**kwargs)


## @brief Represents values with common arithmetic operations
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


## @brief Handles integer fields
# @note Enforcing type to be int
# @note Default name is 'integer' and default 'valueobject' is EmFieldValue_int
class EmField_integer(EmFieldType):

    def __init__(self, **kwargs):
        self._init(kwargs)
        # Default name
        kwargs = self.__class__._argDefault(kwargs, 'name', 'integer')
        # Default value object
        kwargs = self.__class__._argDefault(kwargs, 'valueobject', EmFieldValue_int)
        # Type enforcing
        kwargs = self.__class__._setType(kwargs, 'int')
        super(EmField_integer, self).__init__(**kwargs)

    ##
    # @todo catch cast error ?
    #def to_sql(self, value):
    #    return value

    def to_value(self, value):
        if value == None:
            return super(EmField_integer, self).to_value(value)
        return int(value)


## @brief Handles boolean fields
# @note Enforce type to be 'boolean'
# @note Default name is 'boolean'
class EmField_boolean(EmFieldType):
    def __init__(self, **kwargs):
        self._init(kwargs)
        #Default name
        kwargs = self.__class__._argDefault(kwargs, 'name', 'boolean')
        #Type enforcing
        kwargs = self.__class__._setType(kwargs, 'boolean')
        super(EmField_boolean, self).__init__(**kwargs)

    #def to_sql(self, value):
    #    return 1 if super(EmField_boolean, self).to_sql(value) else 0

    def to_value(self, value):
        if value == None:
            return super(EmField_boolean, self).to_value(value)
        self.value = bool(value)
        return self.value


## @brief Handles string fields
# @note Enforce type to be (varchar)
# @note Default 'name' is 'char'
# @note Default 'type_length' is 76
class EmField_char(EmFieldType):

    default_length = 76

    def __init__(self, **kwargs):
        self._init(kwargs)
        kwargs = self.__class__._argDefault(kwargs, 'type_length', self.__class__.default_length)
        kwargs = self.__class__._argDefault(kwargs, 'name', 'char')
        #Type enforcing
        kwargs = self.__class__._setType(kwargs, 'varchar')
        super(EmField_char, self).__init__(**kwargs)

    #def to_sql(self, value):
    #    return str(value)


## @brief Handles date fields
# @note Enforce type to be 'datetime'
# @todo rename to EmField_datetime
# @todo timezones support
class EmField_date(EmFieldType):
    def __init__(self, **kwargs):
        self._init(kwargs)
        kwargs = self.__class__._argDefault(kwargs, 'name', 'date')
        #Type enforcing
        kwargs = self.__class__._setType(kwargs, 'datetime')
        super(EmField_date, self).__init__(**kwargs)

    #def to_sql(self, value):
    #    return value #thanks to sqlalchemy

    def to_value(self, value):
        if value == None:
            return super(EmField_date, self).to_value(value)
        if isinstance(value, int):
            #assume its a timestamp
            return datetime.fromtimestamp(value)
        if isinstance(value, datetime.datetime):
            return value


## @brief Handles strings with translations
class EmField_mlstring(EmField_char):

    def __init__(self, **kwargs):
        self._init(kwargs)
        kwargs = self.__class__._argDefault(kwargs, 'name', 'mlstr')
        super(EmField_mlstring, self).__init__(**kwargs)

    #def to_sql(self, value):
    #    return value.__str__()

    def to_value(self, value):
        if value == None:
            return super(EmField_mlstring, self).to_value(value)
        if isinstance(value, str):
            return MlString.load(value)
        elif isinstance(value, MlString):
            return value
        raise TypeError("<class str> or <class MlString> excepted. But got "+str(type(value)))


## @brief Handles lodel uid fields
class EmField_uid(EmField_integer):

    def __init__(self, **kwargs):
        self._init(kwargs)
        kwargs = self.__class__._argEnforce(kwargs, 'primarykey', True)
        super(EmField_uid, self).__init__(**kwargs)
