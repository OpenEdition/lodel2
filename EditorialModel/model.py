# -*- coding: utf-8 -*-

## @file editorialmodel.py
# Manage instance of an editorial model

from EditorialModel.classes import EmClass
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField
from EditorialModel.types import EmType



## Manages the Editorial Model
class Model(object):

    component_class = EmClass
    component_fieldgroup = EmFieldGroup
    component_field = EmField
    component_type = EmType

    ## Constructor
    #
    # @param backend unknown: A backend object instanciated from one of the classes in the backend module
    def __init__(self, backend):
        self.backend = backend
        self.components = {'uids':{}, 'class':{}, 'type':{}, 'field':{}, 'fieldgroup':{}}
        self.load()

    @staticmethod
    ## Given a name return an EmComponent child class
    # @param class_name str : The name to identify an EmComponent class
    def emclass_from_name(class_name):
        return getattr(Model, class_name)

    ## Loads the structure of the Editorial Model
    #
    # Gets all the objects contained in that structure and creates a dict indexed by their uids
    def load(self):
        data = self.backend.load()
        for uid, component in data.items():
            cls_name = 'component_' + component['component']
            cls = self.emclass_from_name(cls_name)
            if cls:
                component['uid'] = uid
                # create a dict for the component and one indexed by uids, store instanciated component in it
                self.components[component['component']][uid] = self.components['uids'][uid] = cls(component, self.components)
        # TODO : check integrity

    ## Saves data using the current backend
    def save(self):
        return self.backend.save()

    ## Create a component from a component type and datas
    #
    # @param component_type str : a component type ( component_class, component_fieldgroup, component_field or component_type )
    # @param datas dict : the options needed by the component creation
    def create_component(self, component_type, datas):
        return self.emclass_from_name[component_type].create(datas)

    ## Delete a component
    # @param uid int : Component identifier
    # @throw NoSuchCompoentException
    # @todo unable uid check
    def delete_component(self, uid):
        #if uid not in self.components:
        #    raise NoSuchComponentException()
        return self.components[uid].delete()

    ## Changes the current backend
    #
    # @param backend unknown: A backend object
    def set_backend(self, backend):
        self.backend = backend

    ## Returns a list of all the EmClass objects of the model
    def classes(self):
        return list(self.components['class'].values())
