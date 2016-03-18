# -*- coding: utf-8 -*-
import importlib

class FieldDataHandler(object):

    help_text = 'Generic Field Data Handler'

    ## @brief constructor
    def __init__(self):
        pass

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

    def module_name(self, fieldtype_name):
        return 'leapi.datahandlers.data_fields.%s' % fieldtype_name