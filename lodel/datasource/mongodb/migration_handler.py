# -*- coding: utf-8 -*-

from lodel.datasource.generic.migrationhandler import GenericMigrationHandler
from lodel.datasource.mongodb.datasource import MongoDbDataSource
import lodel.datasource.mongodb.utils as utils
from lodel.editorial_model.components import EmClass, EmField


class MigrationHandlerChangeError(Exception):
    pass


## @brief Modifies a MongoDb database given editorial model changes
class MongoDbMigrationHandler(GenericMigrationHandler):

    ## @brief constructs a MongoDbMigrationHandler
    # @param conn_args dict : a dictionary containing connection options
    # @param **kwargs : extra arguments given to the connection methods
    def __init__(self, conn_args=None, **kwargs):
        if conn_args is None:
            conn_args = {}  # TODO : récupérer les options de connexion dans les settings
            self.connection_name = conn_args['name']
            # del conn_args['module']

        self.db_conn = MongoDbDataSource(self.connection_name)
        self.database = self.db_conn.database
        # TODO Réimplémenter la partie sur les settings
        mh_settings = {}
        self.dryrun = kwargs['dryrun'] if 'dryrun' in kwargs else mh_settings['dryrun']
        self.foreign_keys = kwargs['foreign_keys'] if 'foreign_keys' in kwargs else mh_settings['foreign_keys']
        self.drop_if_exists = kwargs['drop_if_exists'] if 'drop_if_exists' in kwargs else mh_settings['drop_if_exists']
        self._create_default_collections(self.drop_if_exists)

    ## @brief Modify the database given an EM change
    #
    # @param em model : The EditorialModel.model object to provide the global context.
    # @param uid str : The uid of the changed component.
    # @param initial_state dict|None : dict with field name as key and field value as value. Represents the original state. None means it's a creation of a new component.
    # @param new_state dict|None : dict with field name as key and field value as value. Represents the new state. None means it's a component deletion.
    # @throw MigrationHandlerChangeError if the change was refused
    def register_change(self, em, uid, initial_state, new_state):
        if isinstance(em.classes(uid), EmClass):
            collection_name = utils.object_collection_name(em.classes(uid).display_name)
            if initial_state is None:
                self._create_collection(collection_name)
            elif new_state is None:
                self._delete_collection(collection_name)

    def _create_default_collections(self, drop_if_exist=False):
        if_exists = 'drop' if drop_if_exist else 'nothing'
        # Object collection
        collection_name = utils.common_collections['object']
        self._create_collection(collection_name, if_exists=if_exists)
        # TODO triggers ?
        object_collection_name = collection_name

        # TODO collections de relations
        # TODO clés étrangères

    def _create_collection(self, collection_name, if_exists='nothing'):
        if if_exists == 'drop':
            if collection_name in self.database.collection_names():
                self.database[collection_name].drop()
        else:
            if collection_name not in self.database.collection_names():
                self.database.create_collection(collection_name)

        # TODO Relational fields

    def _delete_collection(self, collection_name):
        # TODO : delete the triggers ?
        if collection_name in self.database.collection_names():
            self.database[collection_name].drop()
