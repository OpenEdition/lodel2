# -*- coding: utf-8 -*-
import importlib

class FieldDataHandler(object):

    help_text = 'Generic Field Data Handler'

    ## @brief List fields that will be exposed to the construct_data_method
    _construct_datas_deps = []

    ## @brief constructor
    # @param internal False | str : define whether or not a field is internal
    # @param immutable bool : indicates if the fieldtype has to be defined in child classes of LeObject or if it is designed globally and immutable
    # @param **args
    def __init__(self, internal=False, immutable=False, **args):
        self.internal = internal  # Check this value ?
        self.immutable = bool(immutable)

        for argname, argval in args.items():
            setattr(self, argname, argval)


    ## Fieldtype name
    @staticmethod
    def name(cls):
        return cls.__module__.split('.')[-1]

    ## @brief checks if a fieldtype is internal
    # @return bool
    def is_internal(self):
        return self.internal != False

    ## @brief calls the data_field defined _check_data_value() method
    # @return tuple (value, error|None)
    def check_data_value(self, value):
        return self._check_data_value(value)

    def _check_data_value(self, value):
        return (value, None)

    ## @brief given a field type name, returns the associated python class
    # @param fieldtype_name str : A field type name
    # @return DataField child class
    @staticmethod
    def from_name(fieldtype_name):
        mod = importlib.import_module(FieldDataHandler.module_name(fieldtype_name))
        return mod.EmDataField

    ## @brief get a module name given a fieldtype name
    # @param fieldtype_name str : a field type name
    # @return a string representing a python module name
    @staticmethod
    def module_name(self, fieldtype_name):
        return 'leapi.datahandlers.data_fields.%s' % fieldtype_name

    ## @brief __hash__ implementation for fieldtypes
    def __hash__(self):
        hash_dats = [self.__class__.__module__]
        for kdic in sorted([k for k in self.__dict__.keys() if not k.startswith('_')]):
            hash_dats.append((kdic, getattr(self, kdic)))
        return hash(tuple(hash_dats))
