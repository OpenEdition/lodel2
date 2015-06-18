#-*- coding: utf-8 -*-

from Lodel.utils.mlstring import MlString
from sqlalchemy import Column, INTEGER, BOOLEAN, VARCHAR
import datetime

def get_field_type(name):
    class_name = 'EmField_' + name
    constructor = globals()[class_name]
    instance = constructor()
    return instance

class EmFieldType():

    def __init__(self, name):
        self.name = name
        self.value = None

    def from_python(self, value):
        self.value = value

    # if an attribute is not in the FieldType, try the attributes of the value
    #def __getattr__(self, name):
        #if hasattr(self.value, name):
            #value_attr = getattr(self.value, name)
            #if hasattr(value_attr, '__call__'):
                #def value_method(*args, **kwargs):
                    #result = value_attr(*args, **kwargs)
                    #return result
                #return value_method
            #else:
                #return value_attr

    # str() refer to str() of the value
    #def __str__(self):
        #return str(self.value)

class EmField_integer(EmFieldType):

    def __init__(self):
        super(EmField_integer, self).__init__('integer')

    def from_string(self, value):
        if value == '':
            self.value = 0
        else:
            self.value = int(value)

    def to_sql(self, value = None):
        if value is None:
            value = self.value
        return value

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

    def sql_column(self):
        return "int(11) NOT NULL"

    def sqlalchemy_args(self):
        # TODO Ajouter la prise en charge de la taille max
        return {'type_': INTEGER, 'nullable': False}

class EmField_boolean(EmFieldType):

    def __init__(self):
        super(EmField_boolean, self).__init__('boolean')

    def from_string(self, value):
        if value:
            self.value = True
        else:
            self.value = False

    def to_sql(self, value = None):
        if value is None:
            value = self.value
        return 1 if value else 0

    def sql_column(self):
        return "tinyint(1) DEFAULT NULL"

    def sqlalchemy_args(self):
        return {'type_': BOOLEAN, 'nullable': True, 'default': None}

class EmField_char(EmFieldType):

    def __init__(self):
        super(EmField_char, self).__init__('char')

    def from_string(self, value):
        if value:
            self.value = value
        else:
            self.value = ''

    def to_sql(self, value = None):
        if value is None:
            value = self.value
        return value

    def sql_column(self):
        return "varchar(250) DEFAULT NULL"

    def sqlalchemy_args(self):
        return {'type_': VARCHAR(250), 'nullable': True, 'default': None}

# TODO
class EmField_date(EmFieldType):

    def __init__(self):
        super(EmField_date, self).__init__('date')

    def from_string(self, value):
        if value:
            self.value = value
        else:
            self.value = ''

    def to_sql(self, value = None):
        if value is None:
            value = self.value
        if not value:
            return datetime.datetime.now()
        return value

    def sql_column(self):
        return "varchar(250) DEFAULT NULL"

    def sqlalchemy_args(self):
        return {'type_': VARCHAR(250), 'nullable': True, 'default': None}


class EmField_mlstring(EmFieldType):

    def __init__(self):
        super(EmField_mlstring, self).__init__('mlstring')

    def from_string(self, value):
        self.value = MlString.load(value)

    def to_sql(self, value = None):
        if value is None:
            value = self.value
        return str(value)

    def sql_column(self):
        return "varchar(250) DEFAULT NULL"

    def sqlalchemy_args(self):
        return {'type_': VARCHAR(250), 'nullable': True, 'default': None}
