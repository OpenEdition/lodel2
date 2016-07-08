# -*- coding: utf-8 -*-
from lodel.leapi.datahandlers.base_classes import Reference, MultipleRef, SingleRef, FieldValidationError

from lodel import logger

class Link(SingleRef):
    pass


##@brief Child class of MultipleRef where references are represented in the form of a python list
class List(MultipleRef):

    ##@brief instanciates a list reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool
    # @param kwargs
    def __init__(self, max_length = None, **kwargs):
        super().__init__(**kwargs)

    ##@brief Check value
    # @param value *
    # @return tuple(value, exception)
    def _check_data_value(self, value):
        if isinstance(value, list) or isintance(value, str):
            val, expt = super()._check_data_value(value)
        else:
            return None, FieldValidationError("List or string expected for a list field")
        if not isinstance(expt, Exception):
            val = list(val)
        return val, expt

    def construct_data(self, emcomponent, fname, datas, cur_value):
        emcomponent_fields = emcomponent.fields()
        data_handler = None
        if fname in emcomponent_fields:
            data_handler = emcomponent_fields[fname]
        u_fname = emcomponent.uid_fieldname()
        uidtype = u_fname[0] if isinstance(u_fname, tuple) else u_fname 
        
        if isinstance(cur_value, str):
            value = cur_value.split(',')
            l_value = [uidtype(uid) for uid in value]
            return l_value
        elif isinstance(cur_value, list):
            type_list = str if isinstance(cur_value[0], str) else uidtype
            l_value = list()
            for value in cur_value:
                if isinstance(value,uidtype):
                    l_value.append(value)
                else:
                    raise ValueError("The items must be of the same type, string or %s" % (target.__name__))
            return l_value
        else:
            return None

##@brief Child class of MultipleRef where references are represented in the form of a python set
class Set(MultipleRef):

    ##@brief instanciates a set reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    ##@brief Check value
    # @param value *
    # @return tuple(value, exception)
    def _check_data_value(self, value):
        val, expt = super()._check_data_value(value)
        if not isinstance(expt, Exception):
            val = tuple(set(val))
        return val, expt


##@brief Child class of MultipleRef where references are represented in the form of a python dict
class Map(MultipleRef):

    ##@brief instanciates a dict reference
    # @param allowed_classes list | None : list of allowed em classes if None no restriction
    # @param internal bool : if False, the field is not internal
    # @param kwargs : Other named arguments
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    ##@brief Check value
    # @param value *
    # @return tuple(value, exception)
    def _check_data_value(self, value):
        val, expt = super()._check_data_value(value)
        if not isinstance(value, dict):
            return None, FieldValidationError("Values for dict fields should be dict")
        return (
                None if isinstance(expt, Exception) else value,
                expt)

##@brief This Reference class is designed to handler hierarchy with some constraint
class Hierarch(MultipleRef):
    
    ##@brief Instanciate a data handler handling hierarchical relation with constraints
    # @param back_reference tuple : Here it is mandatory to have a back ref (like a parent field)
    # @param max_depth int | None :  limit of depth
    # @param max_childs int | Nine : maximum number of childs by nodes
    def __init__(self, back_reference, max_depth = None, max_childs = None, **kwargs):
        super().__init__(   back_reference = back_reference,
                            max_depth = max_depth,
                            max_childs = max_childs,
                            **kwargs)

    def _check_data_value(self, value):
        value, expt = super()._check_data_value(value)
        if isinstance(expt, Exception):
            return None, expt
        # determine depth with datasource
