# 
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import datetime

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.editorial_model.components': ['EmClass', 'EmField'],
    'lodel.editorial_model.model': ['EditorialModel'],
    'lodel.leapi.datahandlers.base_classes': ['DataHandler'],
    'lodel.plugin': ['LodelHook'],
    'lodel.logger': 'logger'})

from leapi_dyncode import * #<-- TODO : handle this !!!

from .utils import connect, object_collection_name, mongo_fieldname
from .datasource import MongoDbDatasource
from .exceptions import *

class MigrationHandler(object):

    ## @brief Constructs a MongoDbMigrationHandler
    # @param host str
    # @param port str
    # @param db_name str
    # @param username str
    # @param password str
    # @param charset str
    # @param dry_run bool
    # @param drop_if_exists bool : drops the table if it already exists
    def __init__(self, host, port, db_name, username, password,
        charset='utf-8', dry_run = False, drop_if_exists = False):

        self.database = connect(host, port, db_name, username, password)
        self.dry_run = dry_run
        self.drop_if_exists = drop_if_exists
        self.charset = charset # Useless ?
            
        logger.debug("MongoDb migration handler instanciated on db : \
%s@%s:%s" % (db_name, host, port))
        
    ## @brief Installs the basis collections of the database
    def init_db(self, emclass_list):
        for collection_name in [ object_collection_name(cls)
            for cls in emclass_list]:
            self._create_collection(collection_name)

    ## @brief Creates a collection in the database
    # @param collection_name str
    def _create_collection(self, collection_name):
        existing = self.database.collection_names(
            include_system_collections=False)
        if collection_name in existing:
            if self.drop_if_exists:
                self._delete_collection(collection_name)
                logger.debug("Collection %s deleted before creating \
it again" % collection_name)
                self.database.create_collection(name=collection_name)
            else:
                logger.info("Collection %s allready exists. \
Doing nothing..." % collection_name)
        else:
            self.database.create_collection(name=collection_name)
            logger.debug("Collection %s created" % collection_name)

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
            raise ValueError('An Editorial Model change should have at least one state precised (initial or new), '
                             'none given here')

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
            handler_func = '_'+component_class_name.lower()+'_'+state_change
            if hasattr(self, handler_func):
                getattr(self, handler_func)(model, uid, initial_state, new_state)
        else:
            raise ValueError("The component concerned should be an EmClass or EmField instance, %s given",
                             model.classes(uid).__class__)

    def register_model_state(self, em, state_hash):
        pass

    ## @brief creates a new collection corresponding to a given uid
    # @see register_change()
    def _emclass_new(self, model, uid, initial_state, new_state):
        collection_name = object_collection_name(model.classes(uid))
        self._create_collection(collection_name)

    ## @brief deletes a collection corresponding to a given uid
    # @see register_change()
    def _emclass_delete(self, model, uid, initial_state, new_state):
        collection_name = object_collection_name(model.classes(uid))
        self._delete_collection(collection_name)

    ## @brief creates a new field in a collection
    # @see register_change()
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
        field_name = mongo_fieldname(model.field(uid).name)
        self._delete_field_in_collection(collection_name, field_name)

    ## @brief upgrades a field
    def _emfield_upgrade(self, model, uid, initial_state, new_state):
        collection_name = self._class_collection_name_from_field(model, initial_state)
        field_name = mongo_fieldname(model.field(uid).name)
        self._check_field_in_collection(collection_name, field_name, initial_state, new_state)

    def _check_field_in_collection(self,collection_name, field_name, initial_sate, new_state):
        collection = self.database[collection_name]
        field_name = mongo_fieldname(field_name)
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
        emfield = EmField(field)
        field_name = mongo_fieldname(field)
        self.database[collection_name].update_many({'uid': emfield.get_emclass_uid(), field_name: {'$exists': False}},
                                                   {'$set': {field_name: options['default']}}, False)

    ## @brief Deletes a field in a collection
    # @param collection_name str
    # @param field_name str
    def _delete_field_in_collection(self, collection_name, field_name):
        if field_name != '_id':
            field_name = mongo_fieldname(field_name)
            self.database[collection_name].update_many({field_name: {'$exists': True}},
                                                       {'$unset': {field_name:1}}, False)
