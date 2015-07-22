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

    ## Loads the structure of the Editorial Model
    #
    # Gets all the objects contained in that structure and creates a dict indexed by their uids
    def load(self):
        data = self.backend.load()
        for uid, component in data.items():
            cls_name = 'component_' + component['component']
            cls = getattr(Model, cls_name)
            if cls:
                component['uid'] = uid
                # create a dict for the component and one indexed by uids, store instanciated component in it
                self.components[component['component']][uid] = self.components['uids'][uid] = cls(component)
        # TODO : check integrity

    ## Saves data using the current backend
    def save(self):
        return self.backend.save()

    ## Changes the current backend
    #
    # @param backend unknown: A backend object
    def set_backend(self, backend):
        self.backend = backend

    ## Returns a list of all the EmClass objects of the model
    def classes(self):
        return list(self.components['class'].values())
