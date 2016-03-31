# -*- coding: utf-8 -*-
import importlib


class FieldDataHandler(object):

    help_text = 'Generic Field Data Handler'

    ## @brief List fields that will be exposed to the construct_data_method
    _construct_datas_deps = []

    ## @brief constructor
    # @param internal False | str : define whether or not a field is internal
    # @param immutable bool : indicates if the fieldtype has to be defined in child classes of LeObject or if it is
    #                         designed globally and immutable
    # @param **args
    # @throw NotImplementedError if it is instanciated directly
    def __init__(self, internal=False, immutable=False, **args):
        if self.__class__ == FieldDataHandler:
            raise NotImplementedError("Abstract class")

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
        return self.internal is not False

    ## @brief calls the data_field defined _check_data_value() method
    # @return tuple (value, error|None)
    def check_data_value(self, value):
        return self._check_data_value(value)

    def _check_data_value(self, value):
        return value, None

    ## @brief checks if this class can override the given data handler
    # @param data_handler DataHandler
    # @return bool
    def can_override(self, data_handler):
        if data_handler.__class__.base_type != self.__class__.base_type:
            return False
        return True

    ## @brief Build field value
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname str : The field name
    # @param datas dict : dict storing fields values (from the component)
    # @param cur_value : the value from the current field (identified by fieldname)
    def construct_data(self, emcomponent, fname, datas, cur_value):
        emcomponent_fields = emcomponent.fields()
        fname_data_handler = None
        if fname in emcomponent_fields:
            fname_data_handler = FieldDataHandler.from_name(emcomponent_fields[fname])

        if fname in datas.keys():
            return cur_value
        elif fname_data_handler is not None and hasattr(fname_data_handler, 'default'):
                return fname_data_handler.default
        elif fname_data_handler is not None and fname_data_handler.nullable:
                return None

        raise RuntimeError("Unable to construct data for field %s", fname)

    ## @brief Check datas consistency
    # @param emcomponent EmComponent : An EmComponent child class instance
    # @param fname : the field name
    # @param datas dict : dict storing fields values
    # @return an Exception instance if fails else True
    # @todo A implémenter
    def check_data_consistency(self, emcomponent, fname, datas):
        return True

    ## @brief given a field type name, returns the associated python class
    # @param fieldtype_name str : A field type name
    # @return DataField child class
    @staticmethod
    def from_name(data_handler_name):
        data_handler_name = data_handler_name.lower()
        mod = None
        for mname in FieldDataHandler.modules_name(data_handler_name):
            try:
                mod = importlib.import_module(mname)
            except ImportError:
                pass
        if mod is None:
            raise NameError("Unknown data_handler name : '%s'" % data_handler_name)
        return mod.DataHandler

    ## @brief get a module name given a fieldtype name
    # @param fieldtype_name str : a field type name
    # @return a string representing a python module name
    @staticmethod
    def modules_name(fieldtype_name):
        return (
                'lodel.leapi.datahandlers.data_fields.%s' % fieldtype_name,
                'lodel.leapi.datahandlers.references.%s' % fieldtype_name
        )

    ## @brief __hash__ implementation for fieldtypes
    def __hash__(self):
        hash_dats = [self.__class__.__module__]
        for kdic in sorted([k for k in self.__dict__.keys() if not k.startswith('_')]):
            hash_dats.append((kdic, getattr(self, kdic)))
        return hash(tuple(hash_dats))
