#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from Lodel.utils.mlstring import MlString
from sqlalchemy import Column, INTEGER, BOOLEAN, VARCHAR

def get_field_type(name):
    class_name = 'EmField_' + name
    constructor = globals()[class_name]
    instance = constructor()
    return instance

class EmFieldType():

    def __init__(self, name):
        self.name = name


class EmField_integer(EmFieldType):

    def __init__(self):
        super(EmField_integer, self).__init__('integer')

    def to_python(self, value):
        if value == '':
            self.value = 0
        else:
            self.value = int(value)

    def to_sql(self, value = None):
        if value is None:
            value = self.value
        return str(value)

    def sql_column(self):
        return "int(11) NOT NULL"

    def sqlalchemy_args(self):
        # TODO Ajouter la prise en charge de la taille max
        return {'type_': INTEGER, 'nullable': False}

class EmField_boolean(EmFieldType):

    def __init__(self):
        super(EmField_boolean, self).__init__('boolean')

    def to_python(self, value):
        if value:
            self.value = True
        else:
            self.value = False
        return self.value

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

    def to_python(self, value):
        if value:
            self.value = value
        else:
            self.value = ''
        return self.value

    def to_sql(self, value = None):
        if value is None:
            value = self.value
        return value

    def sql_column(self):
        return "varchar(250) DEFAULT NULL"

    def sqlalchemy_args(self):
        return {'type_': VARCHAR(250), 'nullable': True, 'default': None}


class EmField_mlstring(EmFieldType):

    def __init__(self):
        super(EmField_mlstring, self).__init__('mlstring')

    def to_python(self, value):
        self.value = MlString.load(value)
        return self.value

    def to_sql(self, value = None):
        if value is None:
            value = self.value
        return str(value)

    def sql_column(self):
        return "varchar(250) DEFAULT NULL"

    def sqlalchemy_args(self):
        return {'type_': VARCHAR(250), 'nullable': True, 'default': None}
