#-*- coding: utf-8 -*-

from EditorialModel.fieldtypes import EmField_integer

from Database import sqlutils
import sqlalchemy as sqla

import logging

logger = logging.getLogger('Lodel2.EditorialModel')

## Em_Field_Type (Class)
#
# Represents an association between a field and a type
class Em_Field_Type(object):

    table = 'em_field_type'
    _fields = [('type_id', EmField_integer),('field_id', EmField_integer)]
    dbconf = 'default'

    ## __init__ (Function)
    #
    # Instanciates an Em_Field_Type object with data fetched from the database
    #
    # @param type_id integer: Identifier of the type
    # @param field_id integer: Identifier of the field
    def __init__(self, type_id, field_id):
        self.table = Em_Field_Type.table
        self._fields = self.__class__._fields
        self.type_id = type_id
        self.field_id = field_id

    ## GetDbe (Function)
    #
    # Returns the sqlAlchemy engine
    @classmethod
    def getDbe(cls):
        return sqlutils.getEngine(cls.dbconf)

    ## Create (Function)
    #
    # Creates a relation between a field and a type
    #
    # @static
    #
    # @param emType EmType: Object representing the Type
    # @param emField EmField: Object representing the Field
    # @return Em_Field_Type object
    @classmethod
    def create(cls, emType, emField):
        values = {
                'type_id': emType.uid,
                'field_id': emField.uid
        }

        createdRelation = Em_Field_Type._createDb(**values)
        return createdRelation

    @classmethod
    def _createDb(cls, **kwargs):
        dbe = cls.getDbe()
        conn = dbe.connect()
        table = sqla.Table(cls.table, sqlutils.meta(dbe))
        req = table.insert(kwargs)
        res = conn.execute(req)
        conn.close()
        return Em_Field_Type(kwargs['type_id'], kwargs['field_id'])

    ## Delete (Function)
    #
    # Deletes a relation between a field and a type
    #
    # @return Boolean
    def delete(self):
        return _deleteDb()

    def _deleteDb(self):
        dbe = self.getDbe()
        table = sqla.Table(self.table, sqlutils.meta(dbe))
        req = table.Delete().Where(table.c.type_id==self.type_id).Where(table.c.field_id==self.field_id)
        conn = dbe.connect()
        try:
            conn.execute(req)
            res = True
        except:
            res = False
        conn.close()

        return res

    ## Exists (Function)
    #
    # Checks if a the relation exists in the database
    #
    # @return True if success, False if failure
    def exists(self):
        return _existsDb()

    ## _ExistsDb (Function)
    #
    # Queries the database to see if a relation exists or not
    #
    # @return True if success, False if failure
    def _existsDb(self):
        dbe = self.getDbe()
        table = sqla.Table(self.table, sqlutils.meta(dbe))
        req = table.Select().Where(table.c.type_id==self.type_id).Where(table.c.field_id==self.field_id)
        conn = dbe.connect()
        res = conn.execute(req).fetchall()
        conn.close()
        return len(res)>0