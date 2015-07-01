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
    # @param kwargs dict: Dictionary of the values to insert in the field record
    #
    # @throw TypeError
    # @see EmComponent::__init__()
    # @staticmethod
    @classmethod
    def create(cls, name, fieldgroup, fieldtype, optional=0, internal=0, rel_to_type_id=0, rel_field_id=0, icon=0):
        try:
            exists = EmField(name)
        except EmComponentNotExistError:
            values = {
                'name': name,
                'fieldgroup_id': fieldgroup.uid,
                'fieldtype': fieldtype.name,
                'optional': optional,
                'internal': internal,
                'rel_to_type_id': rel_to_type_id,
                'rel_field_id': rel_field_id,
                'icon': icon
            }

            created_field = super(EmField, cls).create(**values)
            if created_field:
                is_field_column_added = created_field.add_field_column_to_class_table()
                if is_field_column_added:
                    return created_field

            exists = created_field

        return exists

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
        field_type = "%s%s" % (get_field_type(self.fieldtype).sql_column(), " DEFAULT 0" if self.fieldtype == 'integer' else '')
        field_class_table = self.get_class_table()

        sql_engine = sqlutils.getEngine()
        conn = sql_engine.connect()
        meta_data = sqlutils.meta(sql_engine)
        table = sql.Table(field_class_table, meta_data)
        new_column = self.create_column(name=self.name, type_=field_type)
        ddl = AddColumn(table, new_column)
        sql_query = ddl.compile(dialect=sql_engine.dialect)
        sql_query = str(sql_query)
        logger.debug("Executing SQL : '%s'" % sql_query)
        ret = bool(conn.execute(sql_query))
        return ret

    def create_column(self, **kwargs):
        if not 'name' in kwargs or ('type' not in kwargs and 'type_' not in kwargs):
            pass

        if 'type_' not in kwargs and 'type' in kwargs:
            kwargs['type_'] = self.sql_to_sqla_type(kwargs['type'])
            del kwargs['type']

        if 'extra' in kwargs:
            for extra_name in kwargs['extra']:
                kwargs[extra_name] = kwargs['extra']['name']
            del kwargs['extra']

        if 'foreignkey' in kwargs:
            foreign_key = sql.ForeignKey(kwargs['foreignkey'])
            del kwargs['foreignkey']
        else:
            foreign_key = None

        if 'primarykey' in kwargs:
            kwargs['primary_key'] = kwargs['primarykey']
            del kwargs['primarykey']

        result = sql.Column(**kwargs)

        if foreign_key is not None:
            result.append_foreign_key(foreign_key)

        return result

    def sql_to_sqla_type(self, strtype):
        if 'VARCHAR' in strtype:
            check_length = re.search(re.compile('VARCHAR\(([\d]+)\)', re.IGNORECASE), strtype)
            column_length = int(check_length.groups()[0]) if check_length else None
            return sql.VARCHAR(lengh=column_length)
        else:
            try:
                return getattr(sql, strtype)
            except AttributeError:
                raise NameError("Unknown type '%s'" % strtype)

    ## get_class_table (Function)
    #
    # Gets the name of the table of the class corresponding to the field
    #
    # @return Name of the table
    def get_class_table(self):
        return self._get_class_table_db()

    ## _get_class_tableDb (Function)
    #
    # Executes a request to the database to get the name of the table in which to add the field
    #
    # @return Name of the table
    def _get_class_table_db(self):
        dbe = self.db_engine()
        conn = dbe.connect()
        field_group_table = sql.Table(EmFieldGroup.table, sqlutils.meta(dbe))
        request_get_class_id = field_group_table.select().where(field_group_table.c.uid == self.fieldgroup_id)
        result_get_class_id = conn.execute(request_get_class_id).fetchall()
        class_id = dict(zip(result_get_class_id[0].keys(), result_get_class_id[0]))['class_id']

        class_table = sql.Table(EmClass.table, sqlutils.meta(dbe))
        request_get_class_table = class_table.select().where(class_table.c.uid == class_id)
        result_get_class_table = conn.execute(request_get_class_table).fetchall()
        class_table_name = dict(zip(result_get_class_table[0].keys(), result_get_class_table[0]))['name']

        return class_table_name
