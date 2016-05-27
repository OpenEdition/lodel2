# -*- coding: utf-8 -*-

import datetime

from lodel.leapi.datahandlers.base_classes import DataHandler
from lodel.datasource.generic.migrationhandler import GenericMigrationHandler
import lodel.datasource.mongodb.utils as utils
from lodel.editorial_model.components import EmClass, EmField
from lodel.editorial_model.model import EditorialModel

class MigrationHandlerChangeError(Exception):
    pass


class MongoDbMigrationHandler(GenericMigrationHandler):

    COMMANDS_IFEXISTS_DROP = 'drop'
    COMMANDS_IFEXISTS_NOTHING = 'nothing'

    ## @brief constructs a MongoDbMigrationHandler
    # @param conn_args dict : a dictionary containing connection options
    # @param **kwargs : extra arguments given to the connection method
    def __init__(self, conn_args=None, **kwargs):

        if conn_args is None:
            conn_args = {}  # TODO : get the connection parameters in the settings

        self.connection_name = conn_args['name']

        self.database = utils.mongodbconnect(self.connection_name)

        # === Migration settings ===
        # TODO reimplement the settings management here
        mh_settings = {'dry_run': False, 'foreign_keys': True, 'drop_if_exists': False}
        self.dryrun = kwargs['dryrun'] if 'dryrun' in kwargs else mh_settings['dryrun']
        self.foreign_keys = kwargs['foreign_keys'] if 'foreign_keys' in kwargs else mh_settings['forein_keys']
        self.drop_if_exists = kwargs['drop_if_exists'] if 'drop_if_exists' in kwargs else mh_settings['drop_if_exists']

        self._main_collection_name = 'object'
        self._relation_collection_name = 'relations'

        self._install_tables()

    def _install_tables(self):
        self._create_collection(self._main_collection_name)
        self._create_collection(self._relation_collection_name)

    ## @brief Records a change in the EditorialModel and indicates whether or not it is possible to commit it in the database
    # @note The states contains only the changing fields
    # @param model EditorialModel : The EditorialModel object providing the global context
    # @param uid str : the uid of the changing component
    # @param initial_state dict|None: dict representing the original state ({field_name: field_value, ...}). None means the component is created
    # @param new_state dict|None: dict representing the new state ({field_name: field_value, ...}). None means the component is deleted
    def register_change(self, model, uid, initial_state, new_state):
        if initial_state is None:
            state_change = 'new'
        elif new_state is None:
            state_change = 'del'
        else:
            state_change = 'upgrade'

        component_class_name = model.classes(uid).__class__.name
        handler_func(component_class_name.lower() + '_' + state_change)
        if hasattr(self, handler_func):
            getattr(self, handler_func)(model, uid, initial_state, new_state)

    def register_model_state(self, em, state_hash):
        pass

    def emclass_new(self, model, uid, initial_state, new_state):
        class_collection_name = model.classes(uid).name
        self._create_collection(class_collection_name)

    def emclass_del(self, model, uid, initial_state, new_state):
        emclass = model.classes(uid)
        if not isinstance(emclass, EmClass):
            raise ValueError("The given uid is not an EmClass uid")

        class_collection_name = utils.object.collection_name(emclass.uid)
        self._delete_collection(class_collection_name)

    ## @brief creates a new collection for a new class
    # @param model EditorialModel
    # @param uid str
    # @param initial_state dict|None: dict with field name as key and field value as value. Represents the original state.
    # @param new_state dict|None : dict with field name as key and field value as value. Represents the new state.
    def emfield_new(self, model, uid, initial_state, new_state):
        if new_state['data_handler'] == 'relation':
            # find relational_type name, and class_name of the field
            class_name = self._class_collection_name_from_field(model, new_state)
            self._create_field_in_collection(class_name, uid, new_state)
            return True

        if new_state['internal']:
            # TODO ?
        else:
            collection_name = self._class_collection_name_from_field(model, new_state)

        field_definition = self._field_definition(new_state['data_handler'], new_state)
        self._create_field_in_collection(collection_name, uid, field_definition)

    def emfield_del(self, model, uid, initial_state, new_state):
        if uid != '_id':
            collection_name = self._class_collection_name_from_field(model, initial_state)
            self.database[collection_name].update_many({field:{'$exists':True}}, {'$unset':{field:1}}, False)

    def _field_definition(self, fieldtype, options):
        basic_type = DataHandler.from_name(fieldtype).ftype

        field_definition = {'default_value':None}

        if basic_type == 'datetime':
            if 'now_on_create' in options and options['now_on_create']:
                return {'default': datetime.datetime.utcnow()}
        if basic_type == 'relation':
            return {'default' : []}

        return {'default': ''}

    def _class_collection_name_from_field(self, model, field):
        class_id = field['class_id']
        class_name = model.classes(class_id).name
        class_collection_name = utils.object_collection_name(class_name)
        return class_collection_name

    def _create_collection(self, collection_name, charset='utf8', if_exists=MongoDbMigrationHandler.COMMANDS_IFEXISTS_NOTHING):
        if if_exists == self.__class__.COMMANDS_IFEXISTS_DROP:
            if collection_name in self.database.collection_names(include_system_collections = False):
                self._delete_collection(collection_name)
        self.database.create_collection(name=collection_name)

    def _delete_collection(self, collection_name):
        collection = self.database[collection_name]
        collection.drop_indexes()
        collection.drop()

    def _create_field_in_collection(self, collection_name, field, options):
        self.database[collection_name].update_many({field: {'$exists': False}}, {'$set': {field: options['default']}},
                                                   False)

    def _add_fk(self, src_collection_name, dst_collection_name, src_field_name, dst_field_name, fk_name=None):
        if fk_name is None:
            fk_name = utils.get_fk_name(src_collection_name, dst_collection_name)
        self._del_fk(src_collection_name, dst_collection_name, fk_name)

        self.database[src_collection_name].update_many({fk_name: {'$exists': False}}, {'$set': {fk_name: []}}, False)

    def del_fk(self, src_collection_name, dst_collection_name, fk_name=None):
        if fk_name is None:
            fk_name = utils.get_fk_name(src_collection_name, dst_collection_name)
        self.database[src_collection_name].update_many({}, {'$unset': {fk_name:1}}, False)
