# -*- coding: utf-8 -*-

## @file classes.py
# @see EditorialModel::classes::EmClass

from EditorialModel.components import EmComponent
import EditorialModel.fieldtypes as ftypes
import EditorialModel

## @brief Manipulate Classes of the Editorial Model
# Create classes of object.
# @see EmClass, EmType, EmFieldGroup, EmField
# @todo sortcolumn handling
class EmClass(EmComponent):

    table = 'em_class'
    ranked_in = 'classtype'

    ## @brief Specific EmClass fields
    # @see EditorialModel::components::EmComponent::_fields
    _fields = [
        ('classtype', ftypes.EmField_char),
        ('icon', ftypes.EmField_icon),
        ('sortcolumn', ftypes.EmField_char)
    ]

    ## Create a new class
    # @param name str: name of the new class
    # @param class_type EmClasstype: type of the class
    # @return an EmClass instance
    # @throw EmComponentExistError if an EmClass with this name and a different classtype exists
    @classmethod
    def create(cls, name, classtype, icon=None, sortcolumn='rank', **em_component_args):
        pass
        # return cls._create_db(name=name, classtype=classtype['name'], icon=icon, sortcolumn=sortcolumn, **em_component_args)

    # @classmethod
    # def _create_db(cls, name, classtype, icon, sortcolumn, **em_component_args):
    #     result = super(Em, cls).create(name=name, classtype=classtype, icon=icon, sortcolumn=sortcolumn, **em_component_args)
    #
    #     dbe = result.db_engine
    #     conn= dbe.connect()
    #
    #     meta = sql.MetaData()
    #     emclasstable = sql.Table(result.class_table_name, meta, sql.Column('uid', sql.VARCHAR(50), primary_key=True))
    #     emclasstable.create(conn)
    #     conn.close()
    #     return result

    @property
    ## @brief Return the table name used to stores data on this class
    def class_table_name(self):
        return self.name

    ## @brief Delete a class if it's ''empty''
    # If a class has no fieldgroups delete it
    # @return bool : True if deleted False if deletion aborded
    def delete(self):
        pass
        # fieldgroups = self.fieldgroups()
        # if len(fieldgroups) > 0:
        #     return False
        #
        # dbe = self.db_engine
        # meta = sqlutils.meta(dbe)
        # Here we have to give a connection
        # class_table = sql.Table(self.name, meta)
        # meta.drop_all(tables=[class_table], bind=dbe)
        # return super(EmClass, self).delete()

    ## Retrieve list of the field_groups of this class
    # @return A list of fieldgroups instance
    def fieldgroups(self):
        records = self._fieldgroups_db()  # TODO Modifier l'appel
        fieldgroups = [EditorialModel.fieldgroups.EmFieldGroup(int(record.uid)) for record in records]

        return fieldgroups

    ## Isolate SQL for EmClass::fieldgroups
    # @return An array of dict (sqlalchemy fetchall)
    # def _fieldgroups_db(self):
    #     dbe = self.db_engine
    #     emfg = sql.Table(EditorialModel.fieldgroups.EmFieldGroup.table, sqlutils.meta(dbe))
    #     req = emfg.select().where(emfg.c.class_id == self.uid)
    #
    #     conn = dbe.connect()
    #     res = conn.execute(req)
    #     return res.fetchall()

    ## Retrieve list of fields
    # @return fields [EmField]:
    def fields(self):
        fieldgroups = self.fieldgroups()
        fields = []
        for fieldgroup in fieldgroups:
            fields += fieldgroup.fields()
        return fields

    ## Retrieve list of type of this class
    # @return types [EmType]:
    def types(self):
        pass
        records = self._types_db()  # TODO Modifier l'appel
        types = [EditorialModel.types.EmType(int(record.uid)) for record in records]

        return types

    ## Isolate SQL for EmCLass::types
    # @return An array of dict (sqlalchemy fetchall)
    # def _types_db(self):
    #     dbe = self.db_engine
    #     emtype = sql.Table(EditorialModel.types.EmType.table, sqlutils.meta(dbe))
    #     req = emtype.select().where(emtype.c.class_id == self.uid)
    #     conn = dbe.connect()
    #     res = conn.execute(req)
    #     return res.fetchall()

    ## Add a new EmType that can ben linked to this class
    # @param  em_type EmType: type to link
    # @return success bool: done or not
    def link_type(self, em_type):
        table_name = self.name + '_' + em_type.name
        self._link_type_db(table_name)  # TODO Modifier l'appel

        return True

    # def _link_type_db(self, table_name):
        #  Create a new table storing additionnal fields for the relation between the linked type and this EmClass
        # conn = self.db_engine.connect()
        # meta = sql.MetaData()
        # emlinketable = sql.Table(table_name, meta, sql.Column('uid', sql.VARCHAR(50), primary_key=True))
        # emlinketable.create(conn)
        # conn.close()


    ## Retrieve list of EmType that are linked to this class
    #  @return types [EmType]:
    def linked_types(self):
        return self._linked_types_db()  # TODO Modifier l'appel

    # def _linked_types_db(self):
    #     dbe = self.db_engine
    #     meta = sql.MetaData()
    #     meta.reflect(dbe)
    #
    #     linked_types = []
    #     for table in meta.tables.values():
    #         table_name_elements = table.name.split('_')
    #         if len(table_name_elements) == 2:
    #             linked_types.append(EditorialModel.types.EmType(table_name_elements[1]))
    #
    #     return linked_types