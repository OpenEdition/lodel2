# -*- coding: utf-8 -*-

## @file editorialmodel.py
# Manage instance of an editorial model

from EditorialModel.classes import EmClass


class Model(object):

    componentClass = EmClass

    ## Constructor
    #
    # @param backend unknown: A backend object instanciated from one of the classes in the backend module
    def __init__(self, backend):
        self.backend = backend
        self.uids = {}
        self.load()

    ## Loads the structure of the Editorial Model
    #
    # Gets all the objects contained in that structure and creates a list indexed by their uids
    def load(self):
        data = self.backend.load()
        for uid, component in data.items():
            cls_name = 'component' + component['component']
            cls = getattr(Model, cls_name)
            if cls:
                component['uid'] = uid
                self.uids[uid] = cls(component)

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
        classes = [component for _, component in self.uids if isinstance(component, EmClass)]
        return classes
