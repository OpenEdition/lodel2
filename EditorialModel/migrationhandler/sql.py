# -*- coding: utf-8 -*-

## @package EditorialModel.migrationhandler.sql
# @brief A dummy migration handler
#
# According to it every modifications are possible
#

import EditorialModel
from EditorialModel.migrationhandler.dummy import DummyMigrationHandler
from EditorialModel.model import Model
from mosql.db import Database
from Lodel.utils.mosql import create, alter_add


## Manage Model changes
class SQLMigrationHandler(DummyMigrationHandler):

    fieldtype_to_sql = {
        'char': "CHAR(255)",
        'int': 'INT'
    }

    def __init__(self, module=None, *conn_args, **conn_kargs):
        self.db = Database(module, *conn_args, **conn_kargs)
        super(SQLMigrationHandler, self).__init__(False)
        self._pk_column = EditorialModel.classtypes.pk_name() + ' INT PRIMARY_KEY AUTOINCREMENT NOT NULL'
        # @todo vérification de l'existance de la table objects et de la table relation
        self._install_tables()

    ## @brief Record a change in the EditorialModel and indicate wether or not it is possible to make it
    # @note The states ( initial_state and new_state ) contains only fields that changes
    # @param model model : The EditorialModel.model object to provide the global context
    # @param uid int : The uid of the change EmComponent
    # @param initial_state dict | None : dict with field name as key and field value as value. Representing the original state. None mean creation of a new component.
    # @param new_state dict | None : dict with field name as key and field value as value. Representing the new state. None mean component deletion
    # @throw EditorialModel.exceptions.MigrationHandlerChangeError if the change was refused
    def register_change(self, model, uid, initial_state, new_state):
        #print(uid, initial_state, new_state)
        # find type of component change
        component = Model.name_from_emclass(type(model.component(uid)))
        #print ("ça", component, type(model.component(uid)))
        if initial_state is None:
            state_change = 'new'
        elif new_state is None:
            state_change = 'del'
        else:
            state_change = 'upgrade'

        if component == 'EmType' and len(new_state) == 1:
            if 'superiors_list' in new_state:
                what = 'superiors_list'
            elif 'fields_list' in new_state:
                what = 'fields_list'
        else:
            what = component

        handler_func = what + '_' + state_change
        #print (handler_func)
        if hasattr(self, handler_func):
            getattr(self, handler_func)(model, uid, initial_state, new_state)
        #print(handler_func, uid, initial_state, new_state)

    # New Class, a table must be created
    def EmClass_new(self, model, uid, initial_state, new_state):
        class_table_name = self._class_table_name(new_state['name'])
        self._query_bd(
            create(table=class_table_name, column=self._pk_column)
        )

    # New Field, must create a column in Class table or in Class_Type relational attribute table
    def EmField_new(self, model, uid, initial_state, new_state):
        # field is internal, create a column in the objects table
        if new_state['internal']:
            return
        # field is of type rel2type, create the relational class_type table
        elif new_state['fieldtype'] == 'rel2type':
            # find relational_type name, and class name of the field
            class_name = self._class_table_name_from_field(model, new_state)
            type_name = model.component(new_state['rel_to_type_id']).name
            table_name = class_name + '_' + type_name
            self._query_bd(
                create(table=table_name, column=self._pk_column),
            )
            #print('create rel2type table', class_name, type_name)
            return
        # field is relational (rel_field_id), create a column in the class_type table
        elif new_state['rel_field_id']:
            class_name = self._class_table_name_from_field(model, new_state)
            rel_type_id = model.component(new_state['rel_field_id']).rel_to_type_id
            type_name = model.component(rel_type_id).name
            table_name = class_name + '_' + type_name
            #print('create field in rel2type table', new_state, class_name, rel_type_id, type_name)
        # else create a column in the class table
        else:
            # find name of the class table, and type of the field
            table_name = self._class_table_name_from_field(model, new_state)

        fieldtype = SQLMigrationHandler.fieldtype_to_sql[new_state['fieldtype']]
        self._query_bd(
            alter_add(table=table_name, column=new_state['name'] + ' ' + fieldtype)
        )

    # Test if internal tables must be created, create it if it must
    def _install_tables(self):
        self._query_bd(
            create(table='object', column=self._pk_column),
            create(table='relation', column=('id_relation INT PRIMARY_KEY AUTOINCREMENT NOT NULL', 'id_superior INT', 'id_subdordinate INT', 'nature CHAR(255)', 'depth INT', 'rank INT'))
        )

    def _query_bd(self, *queries):
        with self.db as cur:
            for query in queries:
                print(query)
                cur.execute(query)

    def _class_table_name(self, class_name):
        return class_name

    def _class_table_name_from_field(self, model, field):
        fieldgroup_id = model.component(field['fieldgroup_id']).class_id
        class_name = model.component(fieldgroup_id).name
        class_table_name = self._class_table_name(class_name)
        return class_table_name
