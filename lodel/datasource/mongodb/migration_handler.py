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

    INIT_COLLECTIONS_NAMES = ['object', 'relation', 'entitie', 'person', 'text', 'entry']

    ## @brief constructs a MongoDbMigrationHandler
    # @param conn_args dict : a dictionary containing the connection options
    # @param **kwargs : extra arguments
    def __init__(self, conn_args=None, **kwargs):

        if conn_args is None:
            conn_args = utils.get_connection_args()

        self.connection_name = conn_args['name']
        self.database = utils.mongodbconnect(self.connection_name)

        # TODO : get the following parameters in the settings ?
        migrationhandler_settings = {'dry_run': False, 'foreign_keys': True, 'drop_if_exists': False}

        self.dryrun = kwargs['dryrun'] if 'dryrun' in kwargs else migrationhandler_settings['dry_run']
        self.foreign_keys = kwargs['foreign_keys'] if 'foreign_keys' in kwargs else migrationhandler_settings['foreign_keys']
        self.drop_if_exists = kwargs['drop_if_exists'] if 'drop_if_exists' in kwargs else migrationhandler_settings['drop_if_exists']

        self._install_collections()

    def _install_collections(self):
        for collection_name in MongoDbMigrationHandler.INIT_COLLECTIONS_NAMES:
            collection_to_create = "%s%s" % ('class_', collection_name)
            self._create_collection(collection_name=collection_to_create)

    ## @brief Performs a change in the EditorialModel and indicates
    # @note The states contains only the changing fields in the form of a dict : {field_name1: fieldvalue1, ...}
    # @param model EditorialModel
    # @param uid str : the uid of the changing component
    # @param initial_state dict|None: dict representing the original state, None means the component will be created
    # @param new_state dict|None: dict representing the new state, None means the component will be deleted
    def register_change(self, model, uid, initial_state, new_state):
        if initial_state is not None and new_state is not None:
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
        else:
            pass  # TODO manage the case where no state at all was given

    def register_model_state(self, em, state_hash):
        pass

    ## @brief creates a new collection corresponding to a given uid
    def emclass_new(self, model, uid, initial_state, new_state):
        emclass = model.classes(uid)
        if not isinstance(emclass, EmClass):
            raise ValueError("The given uid is not an EmClass uid")
        collection_name = utils.object_collection_name(emclass)
        self._create_collection(collection_name)

    ## @brief deletes a collection corresponding to a given uid
    def emclass_del(self, model, uid, initial_state, new_state):
        emclass = model.classes(uid)
        if not isinstance(emclass, EmClass):
            raise ValueError("The given uid is not an EmClass uid")
        collection_name = utils.object.collection_name(emclass)
        self._delete_collection(collection_name)

    ## @brief creates a new field in a collection
    # @param model EditorialModel
    # @param uid str
    # @param initial_state dict|None: dict representing the original state
    # @param new_state dict|None: dict representing the new state
    def emfield_new(self, model, uid, initial_state, new_state):
        if new_state['data_handler'] == 'relation':
            # find relational_type name, and class_name of the field
            class_name = self._class_collection_name_from_field(model, new_state)
            self._create_field_in_collection(class_name, uid, new_state)
        else:
            collection_name = self._class_collection_name_from_field(model, new_state)
            field_definition = self._field_defition(new_state['data_handler'], new_state)
            self._create_field_in_collection(collection_name, uid, field_definition)

    ## @brief deletes a field in a collection
    # @param model EditorialModel
    # @param uid str
    # @param initial_state dict|None: dict representing the original state
    # @param new_state dict|None: dict representing the new state
    def emfield_del(self, model, uid, initial_state, new_state):
        collection_name = self._class_collection_name_from_field(model, initial_state)
        field_name = model.field(uid).name
        self._delete_field_in_collection(collection_name, field_name)

    ## @brief Defines the default value when a new field is added to a collection's items
    # @param fieldtype str : name of the field's type
    # @param options dict : dictionary giving the options to use to initiate the field's value.
    # @return dict (containing a 'default' key with the default value)
    def _field_definition(self, fieldtype, options):
        basic_type = DataHandler.from_name(fieldtype).ftype
        if basic_type == 'datetime':
            if 'now_on_create' in options and options['now_on_create']:
                return {'default': datetime.datetime.utcnow()}
        if basic_type == 'relation':
            return {'default': []}

        return {'default': ''}

    def _class_collection_name_from_field(self, model, field):
        class_id = field['class_id']
        component_class = model.classes(class_id)
        component_collection = utils.object_collection_name(component_class)
        return component_collection

    ## @brief Creates a new collection in MongoDb Database
    # @param collection_name str
    # @param charset str
    # @param if_exists str : defines the behavior when the collection already exists (default : 'nothing')
    def _create_collection(self, collection_name, charset='utf8', if_exists=MongoDbMigrationHandler.COMMANDS_IFEXISTS_NOTHING):
        if collection_name in self.database.collection_names(include_system_collections=False):
            # The collection already exists
            if if_exists == MongoDbMigrationHandler.COMMANDS_IFEXISTS_DROP:
                self._delete_collection(collection_name)
                self.database.create_collection(name=collection_name)
        else:
            self.database.create_collection(name=collection_name)

    ## @brief Delete an existing collection in MongoDb Database
    # @param collection_name str
    def _delete_collection(self, collection_name):
        collection = self.database[collection_name]
        collection.drop_indexes()
        collection.drop()

    ## @brief Creates a new field in a collection
    # @param collection_name str
    # @param field str
    # @param options dict
    def _create_field_in_collection(self, collection_name, field, options):
        self.database[collection_name].update_many({field: {'$exists': False}}, {'$set': {field: options['default']}}, False)

    ## @brief Deletes a field in a collection
    # @param collection_name str
    # @param field_name str
    def _delete_field_in_collection(self, collection_name, field_name):
        if field_name != '_id':
            self.database[collection_name].update_many({field_name:{'$exists': True}}, {'$unset':{field_name:1}}, False)
