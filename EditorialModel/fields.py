#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from Database import sqlutils
from Database.sqlwrapper import SqlWrapper
from Database.sqlquerybuilder import SqlQueryBuilder

import sqlalchemy as sql

import EditorialModel
import logging

logger = logging.getLogger('Lodel2.EditorialModel')

"""Represent one data for a lodel2 document"""
class EmField(EmComponent):

    table = 'em_field'

    ## __init__ (Function)
    #
    # Instanciates an EmField object with data fetched from the database
    #
    # @param id_or_name str\int: Identifier of the EmField (global_id or name)
    # @throw TypeError
    # @see EmComponent::__init__()
    def __init__(self, id_or_name):
        self.table = EmField.table
        super(EmField, self).__init__(id_or_name)

    ## Create (Function)
    #
    # Creates a new EmField and instanciates it
    #
    # @static
    #
    # @param name str: The name of the new Type
    # @param em_fieldgroup EmFieldGroup: The new field will belong to this fieldgroup
    # @param em_fieldtype EmFieldType: The new field will have this type
    # @param optional bool: Is the field optional ?
    # @param optional bool: Is the field internal ?
    #
    # @throw TypeError
    # @see EmComponent::__init__()
    # @staticmethod
    @classmethod
    def create(c, name, em_fieldgroup, em_fieldtype, optional=True, internal=False):
        try:
            exists = EmField(name)
        except EmComponentNotExistError:
            values = {
                'uid' : None,
                'name' : name,
                'fieldgroup_id' : em_fieldgroup.id,
                'fieldtype' : em_fieldtype.name,
                'optional' : 1 if optional else 0,
                'internal' : 1 if internal else 0,
            }

            createdField = super(EmField,c).create(**values)
            if createdField:
                # The field was created, we then add its column in the corresponding class' table
                is_field_column_added = EmField.addFieldColumnToClassTable(createdField)
                if is_field_column_added:
                    return createdField

            exists = createdField

        return exists


    ## addFieldColumnToClassTable (Function)
    #
    # Adds a column representing the field in its class' table
    #
    # @static
    #
    # @param emField EmField: the object representing the field
    # @return True in case of success, False if not
    @classmethod
    def addFieldColumnToClassTable(cls, emField):
        field_type = EditorialModel.fieldtypes.get_field_type(emField.em_fieldtype)
        field_sqlalchemy_args = field_type.sqlalchemy_args()
        field_sqlalchemy_args['name'] = emField.name
        field_sqlalchemy_column_object = sqlwrapper.createColumn(**field_sqlalchemy_args)
        field_uid = emField.uid
        field_class_table = emField.get_class_table()
        return sqlwrapper.addColumnObject(tname=field_class_table, column=field_sqlalchemy_column_object)

    ## get_class_table (Function)
    #
    # Gets the name of the table of the class corresponding to the field
    #
    # @return Name of the table
    def get_class_table(self):
        return self._get_class_tableDb()

    ## _get_class_tableDb (Function)
    #
    # Executes a request to the database to get the name of the table in which to add the field
    #
    # @return Name of the table
    def _get_class_tableDb(self):
        dbe = self.getDbE()
        uidtable = sql.Table('uids', sqlutils.meta(dbe))
        conn = dbe.connect()
        sql_wrapper = SqlWrapper(read_db='default', write_db='default', alchemy_logs=False)
        columns=('table')
        query_builder = SqlQueryBuilder(sql_wrapper,'uids')
        query_builder.Select(columns)
        query_builder.From(uidtable)
        query_builder.Where('uids.uid=%s' % self.uid)

        records = query.Execute().fetchall()
        table_records = []
        for record in records:
            table_records.append(dict(zip(record.keys(), record)))
        table_record = table_records[0]
        table_name = table_record['table']

        return table_name

    ## Populate (Function)
    #
    # Sets the object's properties using the values from the database
    def populate(self):
        row = super(EmField, self).populate()
        self.em_fieldgroup = EditorialModel.fieldgroups.EmFieldGroup(int(row.fieldgroup_id))
        self.em_fieldtype = EditorialModel.fieldtypes.get_field_type(row.fieldtype)
        self.optional = True if row.optional == 1 else False;
        self.internal = True if row.internal == 1 else False;
        self.icon = row.icon
        self.rel_to_type_id = EditorialModel.fieldtypes.EmFieldType(int(row.rel_to_type_id)) if row.rel_to_type_id else None
        self.rel_field_id = EmField(int(row.rel_field_id)) if row.rel_field_id else None

    ## Save (Function)
    #
    # Saves the properties of the object as a record in the database
    #
    # @return True in case of success, False if not
    def save(self):
        # should not be here, but cannot see how to do this
        if self.name is None:
            self.populate()

        values = {
            'fieldgroup_id' : self.em_fieldgroup.id,
            'fieldtype' : self.em_fieldtype.name,
            'optional' : 1 if self.optional else 0,
            'internal' : 1 if self.internal else 0,
            'icon' : self.icon,
            'rel_to_type_id' : self.rel_to_type_id.id if self.rel_to_type_id is not None else None,
            'rel_field_id' : self.rel_field_id.id if self.rel_field_id is not None else None
        }

        return super(EmField, self).save(values)

class EmFieldNotExistError(Exception):
    pass