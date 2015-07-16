# -*- coding: utf-8 -*-

## @file editorialmodel.py
# Manage instance of an editorial model

from EditorialModel.classes import EmClass

class Model(object):
    componentClass = EmClass

    def __init__(self, backend):
        self.backend = backend
        self.load()

    def load(self):
        data = self.backend.load()
        self.uids = {}
        for uid, component in data.items():
            cls_name = 'component' + component['component']
            cls = getattr(Model, cls_name)
            if cls:
                component['uid'] = uid
                self.uids[uid] = cls(component)

    # save data using the current backend
    def save(self):
        return self.backend.save()

    # change the current backend
    def set_backend(self, backend):
        self.backend = backend

    # return a list of all EmClass of the model
    def classes():
        classes = [component for component in self.data.uids if isinstance(component, EmClass)]
        return classes
