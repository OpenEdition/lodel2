# -*- coding: utf-8 -*-

## @file editorialmodel.py
# Manage instance of an editorial model

from EditorialModel.classes import EmClass
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField
from EditorialModel.types import EmType



## Manages the Editorial Model
class Model(object):

    componentClass = EmClass
    componentFieldGroup = EmFieldGroup
    componentField = EmField
    componentType = EmType

    ## Constructor
    #
    # @param backend unknown: A backend object instanciated from one of the classes in the backend module
    def __init__(self, backend):
        self.backend = backend
        self.uids = {}
        self.Class = {}
        self.FieldGroup = {}
        self.Field = {}
        self.Type = {}
        self.load()

    ## Loads the structure of the Editorial Model
    #
    # Gets all the objects contained in that structure and creates a dict indexed by their uids
    def load(self):
        data = self.backend.load()
        for uid, component in data.items():
            cls_name = 'component' + component['component']
            cls = getattr(Model, cls_name)
            if cls:
                component['uid'] = uid
                self.uids[uid] = cls(component)
                # create a dict for each component
                getattr(self, component['component'])[uid] = self.uids[uid]
        # TODO
        # iterate over classes, link to subordinates types
        # iterate over types, attach them to classes
        # iterate over fieldgroups, attach them to classes
        # iterate over fields, attach them to fieldgroups, link to types, link to relational fields

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
        return list(self.Class.values())
