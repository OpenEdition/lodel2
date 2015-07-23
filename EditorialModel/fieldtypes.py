#-*- coding: utf-8 -*-

from Lodel.utils.mlstring import MlString
import datetime

## get_field_type (Function)
#
# returns an instance of the corresponding EmFieldType child class for a given name
#
# @param name str: name of the field type
# @return EmFieldType
def get_field_type(name):
    class_name = 'EmField_' + name
    constructor = globals()[class_name]
    instance = constructor()
    return instance


## EmFieldType (Class)
#
# Generic field type
class EmFieldType():

    def __init__(self, name):
        self.name = name
        self.value = None

    def from_python(self, value):
        self.value = value


## EmField_integer (Class)
#
# Integer field type
class EmField_integer(EmFieldType):

    def __init__(self):
        super(EmField_integer, self).__init__('integer')

    def from_string(self, value):
        if value == '':
            self.value = 0
        else:
            self.value = int(value)

    def to_sql(self, value=None):
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


## EmField_boolean (Class)
#
# Boolean field type
class EmField_boolean(EmFieldType):

    def __init__(self):
        super(EmField_boolean, self).__init__('boolean')

    def from_string(self, value):
        if value and value != "0":
            self.value = True
        else:
            self.value = False

    def to_sql(self, value=None):
        if value is None:
            value = self.value
        return 1 if value else 0

    def sql_column(self):
        return "tinyint(1) DEFAULT NULL"


## EmField_char (Class)
#
# Varchar field type
class EmField_char(EmFieldType):

    def __init__(self):
        super(EmField_char, self).__init__('char')

    def from_string(self, value):
        if value:
            self.value = value
        else:
            self.value = ''

    def to_sql(self, value=None):
        if value is None:
            value = self.value
        return value

    def sql_column(self):
        return "varchar(250) DEFAULT NULL"


## EmField_date (Class)
#
# Date Field type
class EmField_date(EmFieldType):

    def __init__(self):
        super(EmField_date, self).__init__('date')

    def from_string(self, value):
        if value:
            self.value = value
        else:
            self.value = ''

    def to_sql(self, value=None):
        if value is None:
            value = self.value
        if not value:
            return datetime.datetime.now()
        return value

    def sql_column(self):
        return "varchar(250) DEFAULT NULL"


## EmField_mlstring (Class)
#
# mlstring Field type
class EmField_mlstring(EmFieldType):

    def __init__(self):
        super(EmField_mlstring, self).__init__('mlstring')

    def from_string(self, value):
        self.value = MlString.load(value)

    def to_sql(self, value=None):
        if value is None:
            value = self.value
        return str(value)

    def sql_column(self):
        return "varchar(250) DEFAULT NULL"


class EmField_icon(EmFieldType):
    
    def __init__(self):
        super(EmField_icon, self).__init__('icon')
        pass

    def from_string(self,value):
        self.value = value

    def to_sql(self, value=None):
        if value != None:
            value = str(value)
        return value

    def sql_column(self):
        pass


