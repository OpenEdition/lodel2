#-*- coding: utf-8 -*-

## @file editorialmodel.py
# Manage instance of an editorial model

import EditorialModel
from EditorialModel.migrationhandler.dummy import DummyMigrationHandler
from EditorialModel.classes import EmClass
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField
from EditorialModel.types import EmType
from EditorialModel.exceptions import EmComponentCheckError, EmComponentNotExistError, MigrationHandlerChangeError
import hashlib


## Manages the Editorial Model
class Model(object):

    components_class = [EmClass, EmField, EmFieldGroup, EmType]

    ## Constructor
    #
    # @param backend unknown: A backend object instanciated from one of the classes in the backend module
    def __init__(self, backend, migration_handler=None):
        self.migration_handler = DummyMigrationHandler() if migration_handler is None else migration_handler
        self.backend = backend
        self._components = {'uids': {}, 'EmClass': [], 'EmType': [], 'EmField': [], 'EmFieldGroup': []}
        self.load()

    def __hash__(self):
        components_dump = ""
        for _, comp in self._components['uids'].items():
            components_dump += str(hash(comp))
        hashstring = hashlib.new('sha512')
        hashstring.update(components_dump.encode('utf-8'))
        return int(hashstring.hexdigest(), 16)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    @staticmethod
    ## Given a name return an EmComponent child class
    # @param class_name str : The name to identify an EmComponent class
    # @return A python class or False if the class_name is not a name of an EmComponent child class
    def emclass_from_name(class_name):
        for cls in Model.components_class:
            if cls.__name__ == class_name:
                return cls
        return False

    @staticmethod
    ## Given a python class return a name
    # @param cls : The python class we want the name
    # @return A class name as string or False if cls is not an EmComponent child class
    def name_from_emclass(em_class):
        if em_class not in Model.components_class:
            spl = em_class.__module__.split('.')
            if spl[1] == 'fieldtypes':
                return 'EmField'
            return False
        return em_class.__name__

    ## Loads the structure of the Editorial Model
    #
    # Gets all the objects contained in that structure and creates a dict indexed by their uids
    # @todo Change the thrown exception when a components check fails
    # @throw ValueError When a component class don't exists
    def load(self):
        datas = self.backend.load()
        for uid, kwargs in datas.items():
            #Store and delete the EmComponent class name from datas
            cls_name = kwargs['component']
            del kwargs['component']
            
            if cls_name == 'EmField':
                if not 'type' in kwargs:
                    raise AttributeError("Missing 'type' from EmField instanciation")

                cls = EditorialModel.fields.EmField.get_field_class(kwargs['type'])
                del(kwargs['type'])
            else:
                cls = self.emclass_from_name(cls_name)

            if cls:
                kwargs['uid'] = uid
                # create a dict for the component and one indexed by uids, store instanciated component in it
                self._components['uids'][uid] = cls(model=self, **kwargs)
                self._components[cls_name].append(self._components['uids'][uid])
            else:
                raise ValueError("Unknow EmComponent class : '" + cls_name + "'")

        #Sorting by rank
        for component_class in Model.components_class:
            self.sort_components(component_class)

        #Check integrity
        for uid, component in self._components['uids'].items():
            try:
                component.check()
            except EmComponentCheckError as exception_object:
                raise EmComponentCheckError("The component with uid %d is not valid. Check returns the following error : \"%s\"" % (uid, str(exception_object)))
            #Everything is done. Indicating that the component initialisation is over
            component.init_ended()

    ## Saves data using the current backend
    def save(self):
        return self.backend.save(self)

    ## Given a EmComponent child class return a list of instances
    # @param cls EmComponent : A python class
    # @return a list of instances or False if the class is not an EmComponent child
    def components(self, cls):
        key_name = self.name_from_emclass(cls)
        return False if key_name is False else self._components[key_name]

    ## Return an EmComponent given an uid
    # @param uid int : An EmComponent uid
    # @return The corresponding instance or False if uid don't exists
    def component(self, uid):
        return False if uid not in self._components['uids'] else self._components['uids'][uid]

    ## Sort components by rank in Model::_components
    # @param emclass pythonClass : The type of components to sort
    # @throw AttributeError if emclass is not valid
    # @warning disabled the test on component_class because of EmField new way of working
    def sort_components(self, component_class):
        #if component_class not in self.components_class:
        #    raise AttributeError("Bad argument emclass : '" + str(component_class) + "', excpeting one of " + str(self.components_class))

        self._components[self.name_from_emclass(component_class)] = sorted(self.components(component_class), key=lambda comp: comp.rank)

    ## Return a new uid
    # @return a new uid
    def new_uid(self):
        used_uid = [int(uid) for uid in self._components['uids'].keys()]
        return sorted(used_uid)[-1] + 1 if len(used_uid) > 0 else 1

    ## Create a component from a component type and datas
    #
    # @note if datas does not contains a rank the new component will be added last
    # @note datas['rank'] can be an integer or two specials strings 'last' or 'first'
    # @param component_type str : a component type ( component_class, component_fieldgroup, component_field or component_type )
    # @param datas dict : the options needed by the component creation
    # @throw ValueError if datas['rank'] is not valid (too big or too small, not an integer nor 'last' or 'first' )
    # @todo Handle a raise from the migration handler
    # @todo Transform the datas arg in **datas ?
    def create_component(self, component_type, datas):
        
        if component_type == 'EmField':
            if not 'type' in datas:
                raise AttributeError("Missing 'type' from EmField instanciation")
            em_obj = EditorialModel.fields.EmField.get_field_class(datas['type'])
            del(datas['type'])
        else:
            em_obj = self.emclass_from_name(component_type)

        rank = 'last'
        if 'rank' in datas:
            rank = datas['rank']
            del datas['rank']

        datas['uid'] = self.new_uid()
        em_component = em_obj(self, **datas)

        em_component.rank = em_component.get_max_rank() + 1 #Inserting last by default

        self._components['uids'][em_component.uid] = em_component
        self._components[self.name_from_emclass(em_component.__class__)].append(em_component)

        if rank != 'last':
            em_component.set_rank(1 if rank == 'first' else rank)

        #everything done, indicating that initialisation is over
        em_component.init_ended()

        #register the creation in migration handler
        try:
            self.migration_handler.register_change(self, em_component.uid, None, em_component.attr_dump)
        except MigrationHandlerChangeError as exception_object:
            #Revert the creation
            self.components(em_component.__class__).remove(em_component)
            del self._components['uids'][em_component.uid]
            raise exception_object

        self.migration_handler.register_model_state(self, hash(self))

        return em_component

    ## Delete a component
    # @param uid int : Component identifier
    # @throw EmComponentNotExistError
    # @todo unable uid check
    # @todo Handle a raise from the migration handler
    def delete_component(self, uid):
        #register the deletion in migration handler
        self.migration_handler.register_change(self, uid, self.component(uid).attr_dump, None)

        em_component = self.component(uid)
        if not em_component:
            raise EmComponentNotExistError()
        if em_component.delete_check():
            self._components[self.name_from_emclass(em_component.__class__)].remove(em_component)
            del self._components['uids'][uid]
        #Register the new EM state
        self.migration_handler.register_model_state(self, hash(self))
        return True

    ## Changes the current backend
    #
    # @param backend unknown: A backend object
    def set_backend(self, backend):
        self.backend = backend

    ## Returns a list of all the EmClass objects of the model
    def classes(self):
        return list(self._components[self.name_from_emclass(EmClass)])
