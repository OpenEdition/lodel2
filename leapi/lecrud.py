#-*- coding: utf-8 -*-

## @package leapi.lecrud
# @brief This package contains the abstract class representing Lodel Editorial components
#

import importlib
import re

import EditorialModel.fieldtypes.generic

## @brief Main class to handler lodel editorial components (relations and objects)
class _LeCrud(object):
    ## @brief The datasource
    _datasource = None

    ## @brief abstract property to store the fieldtype representing the component identifier
    _uid_fieldtype = None #Will be a dict fieldname => fieldtype
    
    ## @brief will store all the fieldtypes (child classes handle it)
    _fieldtypes_all = None

    ## @brief Stores a regular expression to parse query filters strings
    _query_re = None
    ## @brief Stores Query filters operators
    _query_operators = ['=', '<=', '>=', '!=', '<', '>', ' in ', ' not in ']

    def __init__(self):
        raise NotImplementedError("Abstract class")
 
    ## @brief Given a dynamically generated class name return the corresponding python Class
    # @param name str : a concrete class name
    # @return False if no such component
    @classmethod
    def name2class(cls, name):
        mod = importlib.import_module(cls.__module__)
        try:
            return getattr(mod, name)
        except AttributeError:
            return False

    @classmethod
    def leobject(cls):
        return cls.name2class('LeObject')

    ## @return A dict with key field name and value a fieldtype instance
    @classmethod
    def fieldtypes(cls):
        raise NotImplementedError("Abstract method") #child classes should return their uid fieldtype
    
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

    @classmethod
    def fieldlist(cls):
        return cls.fieldtypes().keys()
    
    ## @brief Retrieve a collection of lodel editorial components
    #
    # @param query_filters list : list of string of query filters (or tuple (FIELD, OPERATOR, VALUE) ) see @ref leobject_filters
    # @param field_list list|None : list of string representing fields see @ref leobject_filters
    # @return A list of lodel editorial components instance
    # @todo think about LeObject and LeClass instanciation (partial instanciation, etc)
    @classmethod
    def get(cls, query_filters, field_list = None):
        if not(isinstance(cls, cls.name2class('LeObject'))) and not(isinstance(cls, cls.name2class('LeRelation'))):
            raise NotImplementedError("Cannot call get with LeCrud")

        if field_list is None or len(field_list) == 0:
            #default field_list
            field_list = cls.default_fieldlist()

        field_list = cls.prepare_field_list(field_list) #Can raise LeApiDataCheckError

        #preparing filters
        filters, relational_filters = cls._prepare_filters(field_list)

        #Fetching datas from datasource
        db_datas = cls._datasource.get(cls, filters, relational_filters)

        return [ cls(**datas) for datas in db_datas]
            
    ## @brief Prepare a field_list
    # @param field_list list : List of string representing fields
    # @return A well formated field list
    # @throw LeApiDataCheckError if invalid field given
    @classmethod
    def _prepare_field_list(cls, field_list):
        ret_field_list = list()
        for field in field_list:
            if cls._field_is_relational(field):
                ret = cls._prepare_relational_field(field)
            else:
                ret = cls._check_field(field)

            if isinstance(ret, Exception):
                err_l.append(ret)
            else:
                ret_field_list.append(ret)

        if len(err_l) > 0:
            raise LeApiDataCheckError(err_l)
        return ret_field_list
     
    ## @brief Check that a relational field is valid
    # @param field str : a relational field
    # @return a nature
    @classmethod
    def _prepare_relational_fields(cls, field):
        raise NotImplementedError("Abstract method")
    
    ## @brief Check that the field list only contains fields that are in the current class
    # @return None if no problem, else returns a list of exceptions that occurs during the check
    @classmethod
    def _check_field(cls, field):
        err_l = list()
        if field not in cls.fieldlist():
            return ValueError("No such field '%s' in %s"%(field, cls.__name__))
        return field

    ## @brief Check if a field is relational or not
    # @param field str : the field to test
    # @return True if the field is relational else False
    @staticmethod
    def _field_is_relational(field):
        return field.startswith('superior.') or field.startswith('subordinate')

    ## @brief Prepare filters for datasource
    # 
    # This method divide filters in two categories :
    #  - filters : standart FIELDNAME OP VALUE filter
    #  - relationnal_filters : filter on object relation RELATION_NATURE OP VALUE
    # 
    # Both categories of filters are represented in the same way, a tuple with 3 elements (NAME|NAT , OP, VALUE )
    # 
    # @param filters_l list : This list can contain str "FIELDNAME OP VALUE" and tuples (FIELDNAME, OP, VALUE)
    # @return a tuple(FILTERS, RELATIONNAL_FILTERS
    #
    # @see @ref datasource_side

    @classmethod
    def _prepare_filters(cls, filters_l):
        filters = list()
        res_filters = list()
        rel_filters = list()
        err_l = list()
        for fil in filters_l:
            if len(fil) == 3 and not isinstance(fil, str):
                filters.append(tuple(fil))
            else:
                filters.append(cls._split_filter(fil))

        for field, operator, value in filters:
            if cls._field_is_relational(field):
                #Checks relational fields
                ret = cls._prepare_relational_field(field)
                if isinstance(ret, Exception):
                    err_l.append(ret)
                else:
                    rel_filters.append((ret, operator, value))
            else:
                #Checks other fields
                ret = cls._check_field(field)
                if isinstance(ret, Exception):
                    err_l.append(ret)
                else:
                    res_filters.append((field,operator, value))

        if len(err_l) > 0:
            raise LeApiDataCheckError(err_l)
        return (res_filters, rel_filters)


    ## @brief Check and split a query filter
    # @note The query_filter format is "FIELD OPERATOR VALUE"
    # @param query_filter str : A query_filter string
    # @param cls
    # @return a tuple (FIELD, OPERATOR, VALUE)
    @classmethod
    def _split_filter(cls, query_filter):
        if cls._query_re is None:
            cls._compile_query_re()

        matches = cls._query_re.match(query_filter)
        if not matches:
            raise ValueError("The query_filter '%s' seems to be invalid"%query_filter)

        result = (matches.group('field'), re.sub(r'\s', ' ', matches.group('operator'), count=0), matches.group('value').strip())
        for r in result:
            if len(r) == 0:
                raise ValueError("The query_filter '%s' seems to be invalid"%query_filter)
        return result

    ## @brief Compile the regex for query_filter processing
    # @note Set _LeObject._query_re
    @classmethod
    def _compile_query_re(cls):
        op_re_piece = '(?P<operator>(%s)'%cls._query_operators[0].replace(' ', '\s')
        for operator in cls._query_operators[1:]:
            op_re_piece += '|(%s)'%operator.replace(' ', '\s')
        op_re_piece += ')'
        cls._query_re = re.compile('^\s*(?P<field>(((superior)|(subordinate))\.)?[a-z_][a-z0-9\-_]*)\s*'+op_re_piece+'\s*(?P<value>[^<>=!].*)\s*$', flags=re.IGNORECASE)
        pass
    

            
class LeApiQueryError(EditorialModel.fieldtypes.generic.FieldTypeDataCheckError):
    pass

class LeApiDataCheckError(EditorialModel.fieldtypes.generic.FieldTypeDataCheckError):
    pass
    
