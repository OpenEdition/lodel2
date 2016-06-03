# -*- coding: utf-8 -*-
import datetime

from lodel.editorial_model.components import EmClass, EmField

from .utils import get_connection_args, mongodbconnect, collection_prefix, object_collection_name
from lodel.leapi.datahandlers.base_classes import DataHandler

class MigrationHandlerChangeError(Exception):
    pass


class MongoDbMigrationHandler(object):

    COMMANDS_IFEXISTS_DROP = 'drop'
    COMMANDS_IFEXISTS_NOTHING = 'nothing'
    INIT_COLLECTIONS_NAMES = ['object', 'relation', 'entitie', 'person', 'text', 'entry']
    MIGRATION_HANDLER_DEFAULT_SETTINGS = {'dry_run': False, 'foreign_keys': True, 'drop_if_exists': False}

    ## @brief Constructs a MongoDbMigrationHandler
    # @param conn_args dict : a dictionary containing the connection options
    # @param **kwargs : extra arguments
    def __init__(self, conn_args=None, **kwargs):
        conn_args = get_connection_args() if conn_args is None else conn_args
        self.connection_name = conn_args['name']
        self.database = mongodbconnect(self.connection_name)
        self.dry_run = kwargs['dry_run'] if 'dry_run' in kwargs else MongoDbMigrationHandler.MIGRATION_HANDLER_DEFAULT_SETTINGS['dry_run']
        self.foreign_keys = kwargs['foreign_keys'] if 'foreign_keys' in kwargs else MongoDbMigrationHandler.MIGRATION_HANDLER_DEFAULT_SETTINGS['foreign_keys']
        self.drop_if_exists = kwargs['drop_if_exists'] if 'drop_is_exists' in kwargs else MongoDbMigrationHandler.MIGRATION_HANDLER_DEFAULT_SETTINGS['drop_if_exists']
        self._install_collections()

    ## @brief Installs the basis collections of the database
    def _install_collections(self):
        for collection_name in MongoDbMigrationHandler.INIT_COLLECTIONS_NAMES:
            prefix = collection_prefix['object'] if collection_name != 'relation' else collection_prefix['relation']
            collection_to_create = "%s%s" % (prefix, collection_name)
            self._create_collection(collection_name=collection_to_create)

    ## @brief Creates a collection in the database
    # @param collection_name str
    # @param charset str : default value is "utf8"
    # @param if_exists str : defines the behavior to have if the collection to create already exists (default value : "nothing")
    def _create_collection(self, collection_name, charset='utf8', if_exists=MongoDbMigrationHandler.COMMANDS_IFEXISTS_NOTHING):
        if collection_name in self.database.collection_names(include_system_collections=False):
            if if_exists == MongoDbMigrationHandler.COMMANDS_IFEXISTS_DROP:
                self._delete_collection(collection_name)
                self.database.create_collection(name=collection_name)
        else:
            self.database.create_collection(name=collection_name)

    ## @brief Deletes a collection in the database
    # @param collection_name str
    def _delete_collection(self, collection_name):
        collection = self.database[collection_name]
        collection.drop_indexes()
        collection.drop()

    ## @brief Performs a change in the Database, corresponding to an Editorial Model change
    # @param model EditorialModel
    # @param uid str : the uid of the changing component
    # @param initial_state dict|None : dictionnary of the initial state of the component, None means it's a creation
    # @param new_state dict|None: dictionnary of the new state of the component, None means it's a deletion
    # @note Only the changing properties are added in these state dictionaries
    # @throw ValueError if no state has been precised or if the component considered in the change is neither an EmClass nor an EmField instance
    def register_change(self, model, uid, initial_state, new_state):

        if initial_state is None and new_state is None:
            raise ValueError('An Editorial Model change should have at least one state precised (initial or new), none given here')

        if initial_state is None:
            state_change = 'new'
        elif new_state is None:
            state_change = 'del'
        else:
            state_change = 'upgrade'

        component_class_name = None
        if isinstance(model.classes(uid), EmClass):
            component_class_name = 'emclass'
        elif isinstance(model.classes(uid), EmField):
            component_class_name = 'emfield'

        if component_class_name:
            handler_func('_'+component_class_name.lower()+'_'+state_change)
            if hasattr(self, handler_func):
                getattr(self, handler_func)(model, uid, initial_state, new_state)
        else:
            raise ValueError("The component concerned in this change should be an EmClass or EmField instance, %s given", model.classes(uid).__class__)

    def register_model_state(self, em, state_hash):
        pass

    ## @brief creates a new collection corresponding to a given uid
    # @see register_change()
    def _emclass_new(self, model, uid, initial_state, new_state):
        collection_name = object_collection_name(model.classes(uid))
        self._create_collection(collection_name)

    ## @brief deletes a collection corresponding to a given uid
    # @see register_change()
    # @todo add a test to prevent the deletion of the basis collections ?
    def _emclass_delete(self, model, uid, initial_state, new_state):
        collection_name = object_collection_name(model.classes(uid))
        self._delete_collection(collection_name)

    ## @brief creates a new field in a collection
    # @see register_change()
    # @todo add the filter parameter to add the field only to the documents corresponding to the given class
    def _emfield_new(self, model, uid, initial_state, new_state):
        if new_state['data_handler'] == 'relation':
            class_name = self.class_collection_name_from_field(model, new_state)
            self._create_field_in_collection(class_name, uid, new_state)
        else:
            collection_name = self._class_collection_name_from_field(model, new_state)
            field_definition = self._field_definition(new_state['data_handler'], new_state)
            self._create_field_in_collection(collection_name, uid, field_definition)

    ## @brief deletes a field in a collection
    # @see register_change()
    def _emfield_del(self, model, uid, initial_state, new_state):
        collection_name = self._class_collection_name_from_field(model, initial_state)
        field_name = model.field(uid).name
        self._delete_field_in_collection(collection_name, field_name)

    ## @brief upgrades a field
    # @todo to be implemented
    def _emfield_upgrade(self, model, uid, initial_state, new_state):
        collection_name = self._class_collection_name_from_field(model, initial_state)
        field_name = model.field(uid).name
        self._check_field_in_collection(collection_name, field_name, , initial_state, new_state)

    def _check_field_in_collection(self,collection_name, field_name, initial_sate, new_state):
        collection = self.database[collection_name]
        cursor = collection.find({field_name: {'$exists': True}}, {field_name: 1})
        for document in cursor:
            # TODO vérifier que le champ contient une donnée compatible (document[field_name])
            pass

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
        component_collection = object_collection_name(component_class)
        return component_collection


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
