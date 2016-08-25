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
        if isinstance(value, list) or isinstance(value, str):
            val, expt = super()._check_data_value(value)
        else:
            return None, FieldValidationError("List or string expected for a list field")
        #if not isinstance(expt, Exception):
        #    val = list(val)

        return val, expt

    def construct_data(self, emcomponent, fname, datas, cur_value):
        return super().construct_data(emcomponent, fname, datas, cur_value)

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
        if isinstance(value, set) or isinstance(value, str):
            val, expt = super()._check_data_value(value)
        else:
            return None, FieldValidationError("Set or string expected for a set field")
        return val, expt
    
    def construct_data(self, emcomponent, fname, datas, cur_value):
        return super().construct_data(emcomponent, fname, datas, cur_value)
    
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

    def construct_data(self, emcomponent, fname, datas, cur_value):
        logger.info('WARNING : not well implemented...list are stored...not dict')
        if cur_value == 'None' or cur_value is None or cur_value == '':
            return None
        emcomponent_fields = emcomponent.fields()
        data_handler = None
        if fname in emcomponent_fields:
            data_handler = emcomponent_fields[fname]
        u_fname = emcomponent.uid_fieldname()
        uidtype = emcomponent.field(u_fname[0]) if isinstance(u_fname, list) else emcomponent.field(u_fname)

        if isinstance(cur_value, str):
            value = cur_value.split(',')
            l_value = [uidtype.cast_type(uid) for uid in value]
        elif isinstance(cur_value, list):
            l_value = list()
            for value in cur_value:
                if isinstance(value,uidtype.cast_type):
                    l_value.append(value)
                else:
                    raise ValueError("The items must be of the same type, string or %s" % (emcomponent.__name__))
        else:
            l_value = None

        if l_value is not None:
            if self.back_ref is not None:
                br_class = self.back_ref[0]
                for br_id in l_value:
                    query_filters = list()
                    query_filters.append((br_class.uid_fieldname()[0], '=', br_id))
                    br_obj = br_class.get(query_filters)
                    if len(br_obj) != 0:
                        br_list = br_obj[0].data(self.back_ref[1])
                        if br_list is None:
                            br_list = list()
                        if br_id not in br_list:
                            br_list.append(br_id)
                            logger.info('The referenced object has to be updated')
        return l_value
##@brief This Reference class is designed to handler hierarchy with some constraint
class Hierarch(MultipleRef):
    
    directly_editable = False
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
        if isinstance(value, list) or isinstance(value, str):
            val, expt = super()._check_data_value(value)
        else:
            return None, FieldValidationError("Set or string expected for a set field")
        return val, expt
    
    def construct_data(self, emcomponent, fname, datas, cur_value):
        return super().construct_data(emcomponent, fname, datas, cur_value)