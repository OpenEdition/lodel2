#-*- coding: utf-8 -*-

## @package leapi.lecrud
# @brief This package contains the abstract class representing Lodel Editorial components
#

import EditorialModel

## @brief Main class to handler lodel editorial components (relations and objects)
class _LeCrud(object):
    ## @brief The datasource
    _datasource = None

    ## @brief abstract property to store the fieldtype representing the component identifier
    _uid_fieldtype = None

    ## @brief Stores a regular expression to parse query filters strings
    _query_re = None
    ## @brief Stores Query filters operators
    _query_operators = ['=', '<=', '>=', '!=', '<', '>', ' in ', ' not in ']

    def __init__(self):
        raise NotImplementedError("Abstract class")
 
    ## @return A dict with key field name and value a fieldtype instance
    @classmethod
    def fieldtypes(cls):
        return {'uid' : cls._uid_fieldtype }
    
    ## @return A dict with fieldtypes marked as internal
    @classmethod
    def fieldtypes_internal(self):
        return { fname: ft for fname, ft in cls.fieldtypes().items() if hasattr(ft, 'internal') and ft.internal }
    
    ## @brief Check fields values
    # @param complete bool : If True expect that datas contains all fieldtypes with no default values
    # @param allow_internal bool : If False consider datas as invalid if a value is given for an internal fieldtype
    # @return None if no errors, else returns a list of Exception instances that occurs during the check
    @classmethod
    def check_datas_errors(cls, complete = False, allow_internal = False, **datas):
        intern_fields_name = cls.fieldtypes_internal().keys()
        fieldtypes = cls.fieldtypes()

        err_l = list()

        for dname, dval in datas.items():
            if not allow_internal and dname in intern_fields_name:
                err_l.append(AttributeError("The field '%s' is internal"%dname))
            if dname not in fieldtypes.keys():
                err_l.append(AttributeError("No field named '%s' in %s"%(dname, cls.__name__)))
            check_ret = cls.fieldtypes[dname].check_error(dval)
            if not(ret is None):
                err_l += check_ret

        if complete:
            #mandatory are fields with no default values
            mandatory_fields = set([ ft for fname, ft in fieldtypes.items() if not hasattr(ft, 'default')])
            #internal fields are considered as having default values (or calculated values)
            mandatory_fields -= intern_fields_name

            missing = mandatory_fields - set(datas.keys())
            if len(missing) > 0:
                for missing_field_name in missing:
                    err_l.append(AttributeError("Value for field '%s' is missing"%missing_field_name))

        return None if len(err_l) == 0 else err_l
    
    ## @brief Check fields values
    # @param complete bool : If True expect that datas contains all fieldtypes with no default values
    # @param allow_internal bool : If False consider datas as invalid if a value is given for an internal fieldtype
    # @throw LeApiDataCheckError if checks fails
    # @return None
    @classmethod
    def check_datas_or_raises(cls, complete = False, allow_internal = False, **datas):
        ret = cls.check_datas_errors(complete, allow_internal, **datas)
        if not(ret is None):
            raise LeApiDataCheckError(ret)

class LeApiDataCheckError(EditorialModel.fieldtypes.generic.FieldTypeDataCheckError):
    pass
    
