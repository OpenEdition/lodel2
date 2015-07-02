#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from EditorialModel.fieldtypes import EmField_boolean, EmField_char, EmField_integer, get_field_type
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.classes import EmClass

from Database import sqlutils
from Database.sqlalter import DropColumn, AddColumn

import sqlalchemy as sql

import logging
import re

logger = logging.getLogger('Lodel2.EditorialModel')


## EmField (Class)
#
# Represents one data for a lodel2 document
class EmField(EmComponent):

    table = 'em_field'
    ranked_in = 'fieldgroup_id'
    _fields = [
        ('fieldtype', EmField_char),
        ('fieldgroup_id', EmField_integer),
        ('rel_to_type_id', EmField_integer),
        ('rel_field_id', EmField_integer),
        ('optional', EmField_boolean),
        ('internal', EmField_boolean),
        ('icon', EmField_integer)
    ]

    ## Create (Function)
    #
    # Creates a new EmField and instanciates it
    #
    # @static
    #
    # @param name str: Name of the field
    # @param fieldgroup EmFieldGroup: Field group in which the field is
    # @param fieldtype EmFieldType: Type of the field
    # @param optional int: is the field optional ? (default=0)
    # @param internal int: is the field internal ? (default=0)
    # @param rel_to_type_id int: default=0
    # @param rel_field_id int: default=0
    # @param icon int: default=0
    # @param **em_component_args : @ref EditorialModel::components::create()
    #
    # @throw TypeError
    # @throw RuntimeError if the associated column creation fails
    # @throw EmComponentExistError if an EmField with this name allready exists in this fieldgroup
    # @see EmComponent::__init__()
    # @staticmethod
    @classmethod
    def create(cls, name, fieldgroup, fieldtype, optional=0, internal=0, rel_to_type_id=0, rel_field_id=0, icon=0, **em_component_args):
        created_field = super(EmField, cls).create(
            name=name,
            fieldgroup_id=fieldgroup.uid,
            fieldtype=fieldtype.name,
            optional=optional,
            internal=internal,
            rel_to_type_id=rel_to_type_id,
            rel_field_id=rel_field_id,
            icon=icon,
            **em_component_args
        )
        if not created_field.add_field_column_to_class_table():
            raise RuntimeError("Unable to create the column for the EmField "+str(created_field))

        return created_field

    ## @brief Delete a field if it's not linked
    # @return bool : True if deleted False if deletion aborded
    # @todo Check if unconditionnal deletion is correct
    def delete(self):
        dbe = self.__class__.db_engine()
        class_table = sql.Table(self.get_class_table(), sqlutils.meta(dbe))
        field_col = sql.Column(self.name)
        ddl = DropColumn(class_table, field_col)
        sqlutils.ddl_execute(ddl, self.__class__.db_engine())
        return super(EmField, self).delete()

    ## add_field_column_to_class_table (Function)
    #
    # Adds a column representing the field in its class' table
    #
    # @param emField EmField: the object representing the field
    # @return True in case of success, False if not
    def add_field_column_to_class_table(self):
        dbe = self.db_engine()
        fieldtype = get_field_type(self.fieldtype)
        new_column = sql.Column(name=self.name, **(fieldtype.sqlalchemy_args()) )
        class_table = sql.Table(self.get_class_table(), sqlutils.meta(dbe))
        ddl = AddColumn(class_table, new_column)
        return sqlutils.ddl_execute(ddl, dbe)

    ## get_class_table (Function)
    #
    # Gets the name of the table of the class corresponding to the field
    #
    # @return Name of the table
    def get_class_table(self):
        #return self._get_class_table_db()
        return self.get_class().class_table_name
    
    ## @brief Get the class that contains this field
    # @return An EmClass instance
    def get_class(self):
        #<SQL>
        dbe = self.db_engine()
        conn = dbe.connect()
        fieldgroup_table = sqlutils.getTable(EmFieldGroup)
        req = fieldgroup_table.select().where(fieldgroup_table.c.uid == self.fieldgroup_id)
        res = conn.execute(req)
        row = res.fetchone()
        #</SQL>
        return EmClass(row['class_id'])

