# -*- coding: utf-8 -*-

## @package EditorialModel.migrationhandler.sql
# @brief A dummy migration handler
#
# According to it every modifications are possible
#

import EditorialModel
from DataSource.dummy.migrationhandler import DummyMigrationHandler
from EditorialModel.fieldtypes.generic import GenericFieldType
from EditorialModel.model import Model
from mosql.db import Database
from Lodel.utils.mosql import create, alter_add


## Manage Model changes
class SQLMigrationHandler(DummyMigrationHandler):

    fieldtype_to_sql = {
        'char': "CHAR(255)",
        'integer': 'INT'
    }

    def __init__(self, module=None, *conn_args, **conn_kargs):
        super(SQLMigrationHandler, self).__init__(False)

        self.db = Database(module, *conn_args, **conn_kargs)
        self._pk_column = (EditorialModel.classtypes.pk_name(), 'INTEGER PRIMARY KEY AUTO_INCREMENT')
        self._main_table_name = 'object'
        self._relation_table_name = 'relation'

        self._install_tables()

    ## @brief Record a change in the EditorialModel and indicate wether or not it is possible to make it
    # @note The states ( initial_state and new_state ) contains only fields that changes
    # @param model model : The EditorialModel.model object to provide the global context
    # @param uid int : The uid of the change EmComponent
    # @param initial_state dict | None : dict with field name as key and field value as value. Representing the original state. None mean creation of a new component.
    # @param new_state dict | None : dict with field name as key and field value as value. Representing the new state. None mean component deletion
    # @throw EditorialModel.exceptions.MigrationHandlerChangeError if the change was refused
    def register_change(self, model, uid, initial_state, new_state):
        # find type of component change
        if initial_state is None:
            state_change = 'new'
        elif new_state is None:
            state_change = 'del'
        else:
            state_change = 'upgrade'

        # call method to handle the database change
        component_name = Model.name_from_emclass(type(model.component(uid)))
        handler_func = component_name.lower() + '_' + state_change
        if hasattr(self, handler_func):
            getattr(self, handler_func)(model, uid, initial_state, new_state)

    # New Class, a table must be created
    def emclass_new(self, model, uid, initial_state, new_state):
        class_table_name = self._class_table_name(new_state['name'])
        self._query_bd(
            create(table=class_table_name, column=[self._pk_column])
        )

    # New Field, must create a column in Class table or in Class_Type relational attribute table
    # @todo common fields creation does not allow to add new common fields. It should
    def emfield_new(self, model, uid, initial_state, new_state):

        # field is of type rel2type, create the relational class_type table and return
        if new_state['fieldtype'] == 'rel2type':
            # find relational_type name, and class name of the field
            class_name = self._class_table_name_from_field(model, new_state)
            type_name = model.component(new_state['rel_to_type_id']).name
            table_name = self._relational_table_name(class_name, type_name)
            self._query_bd(
                create(table=table_name, column=[self._pk_column]),
            )
            return

        # Column creation
        #
        # field is internal, create a column in the objects table
        if new_state['internal']:
            if new_state['fieldtype'] == 'pk':  # this column has already beeen created by self._install_tables()
                return
            if new_state['name'] in EditorialModel.classtypes.common_fields:  # this column has already beeen created by self._install_tables()
                return

        # field is relational (rel_field_id), create a column in the class_type table
        elif new_state['rel_field_id']:
            class_name = self._class_table_name_from_field(model, new_state)
            rel_type_id = model.component(new_state['rel_field_id']).rel_to_type_id
            type_name = model.component(rel_type_id).name
            table_name = self._relational_table_name(class_name, type_name)

        # else create a column in the class table
        else:
            table_name = self._class_table_name_from_field(model, new_state)

        field_definition = self._fieldtype_definition(new_state['fieldtype'], new_state)
        self._query_bd(
            alter_add(table=table_name, column=[(new_state['name'],field_definition)])
        )

    ## convert fieldtype name to SQL definition
    def _fieldtype_definition(self, fieldtype, options):
        basic_type = GenericFieldType.from_name(fieldtype).ftype
        if basic_type == 'int':
            return 'INT'
        elif basic_type == 'char':
            max_length = options['max_length'] if 'max_length' in options else 255
            return 'CHAR(%s)' % max_length
        elif basic_type == 'text':
            return 'TEXT'
        elif basic_type == 'bool':
            return 'BOOLEAN'
        elif basic_type == 'datetime':
            definition = 'DATETIME'
            if 'now_on_create' in options and options['now_on_create']:
                definition += ' DEFAULT CURRENT_TIMESTAMP'
            #if 'now_on_update' in options and options['now_on_update']:
                #definition += ' ON UPDATE CURRENT_TIMESTAMP'
            return definition

        raise EditorialModel.exceptions.MigrationHandlerChangeError("Basic type '%s' of fieldtype '%s' is not compatible with SQL migration Handler" % basic_type, fieldtype)

    ## Test if internal tables must be created, create it if it must
    def _install_tables(self):
        # create common fields definition
        common_fields = [self._pk_column]
        for name, options in EditorialModel.classtypes.common_fields.items():
            if options['fieldtype'] != 'pk':
                common_fields.append((name, self._fieldtype_definition(options['fieldtype'], options)))

        # create common tables
        self._query_bd(
            create(table=self._main_table_name, column=common_fields),
            create(table=self._relation_table_name, column=[('relation_id','INTEGER PRIMARY KEY AUTOINCREMENT'), ('superior_id','INT'), ('subdordinate_id','INT'), ('nature','CHAR(255)'), ('depth','INT'), ('rank','INT')])
        )

    def _query_bd(self, *queries):
        with self.db as cur:
            for query in queries:
                print(query)
                cur.execute(query)

    def _class_table_name(self, class_name):
        return 'class_' + class_name

    def _relational_table_name(self, class_name, type_name):
        return 'r2t_' + class_name + '_' + type_name

    def _class_table_name_from_field(self, model, field):
        class_id = field['class_id']
        class_name = model.component(class_id).name
        class_table_name = self._class_table_name(class_name)
        return class_table_name
