# -*- coding: utf-8 -*-

## @file editorialmodel.py
# Manage instance of an editorial model

from EditorialModel.classes import EmClass
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField
from EditorialModel.types import EmType
import EditorialModel

## Manages the Editorial Model
class Model(object):

    components_class = [ EmClass, EmField, EmFieldGroup, EmType ]

    ## Constructor
    #
    # @param backend unknown: A backend object instanciated from one of the classes in the backend module
    def __init__(self, backend):
        self.backend = backend
        self._components = {'uids':{}, 'EmClass':[], 'EmType':[], 'EmField':[], 'EmFieldGroup':[]}
        self.load()

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
    def name_from_emclass(cls):
        if cls not in Model.components_class:
            return False
        return cls.__name__

    ## Loads the structure of the Editorial Model
    #
    # Gets all the objects contained in that structure and creates a dict indexed by their uids
    def load(self):
        data = self.backend.load()
        for uid, component in data.items():
            cls_name = component['component']
            cls = self.emclass_from_name(cls_name)
            if cls:
                component['uid'] = uid
                # create a dict for the component and one indexed by uids, store instanciated component in it
                self._components['uids'][uid] = cls(component, self)
                self._components[cls_name].append(self._components['uids'][uid])
            else:
                raise ValueError("Unknow EmComponent class : '"+cls_name+"'")

        for emclass in Model.components_class:
            comp_list = self.components(emclass)
            self._components[self.name_from_emclass] = sorted(comp_list, key=lambda cur_comp: cur_comp.rank)

        # TODO : check integrity

    ## Saves data using the current backend
    def save(self):
        return self.backend.save()

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
        
    ## Return a new uid
    # @return a new uid
    def new_uid(self):
        used_uid = self._components.keys()
        return sorted(new_uid)[-1] + 1 if len(used_uid) > 0 else 1

    ## Create a component from a component type and datas
    #
    # @param component_type str : a component type ( component_class, component_fieldgroup, component_field or component_type )
    # @param datas dict : the options needed by the component creation
    def create_component(self, component_type, datas):
        datas['uid'] = self.new_uid
        em_component = self.emclass_from_name(component_type)(datas, self)

        self._components['uids'][em_component.uid] = em_component
        self._components[name_from_emclass(em_component.__class__)].append(em_component)
        return em_component

    ## Delete a component
    # @param uid int : Component identifier
    # @throw EditorialModel.components.EmComponentNotExistError
    # @todo unable uid check
    def delete_component(self, uid):
        if uid not in self._components[uid]:
            raise EditorialModel.components.EmComponentNotExistError()
        em_component = self._components[uid]
        if em_component.delete_p():
            self._components[name_from_emclass(em_component.__class__)].remove(em_component)
            del self._components['uids'][uid]
        return True

    ## Changes the current backend
    #
    # @param backend unknown: A backend object
    def set_backend(self, backend):
        self.backend = backend

    ## Returns a list of all the EmClass objects of the model
    def classes(self):
        return list(self._components[Model.name_from_emclass(EmClass)])
