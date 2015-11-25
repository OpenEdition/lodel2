#-*- coding: utf-8 -*-

## @package leapi.lecrud
# @brief This package contains the abstract class representing Lodel Editorial components
#

import warnings
import importlib
import re

import leapi.leobject

class LeApiErrors(Exception):
    ## @brief Instanciate a new exceptions handling multiple exceptions
    # @param expt_l list : A list of data check Exception
    def __init__(self, msg = "Unknow error", exceptions = None):
        self._msg = msg
        self._exceptions = list() if exceptions is None else exceptions

    def __str__(self):
        msg = self._msg
        for expt in self._exceptions:
            msg += " {expt_name}:{expt_msg}; ".format(expt_name=expt.__class__.__name__, expt_msg=str(expt))
        return msg

    def __repr__(self):
        return str(self)


## @brief When an error concern a query
class LeApiQueryError(LeApiErrors): pass

## @brief When an error concerns a datas
class LeApiDataCheckError(LeApiErrors): pass
    

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
    
    ## @return LeObject class
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
    
    ## @return A list of field name
    @classmethod
    def fieldlist(cls):
        return cls.fieldtypes().keys()
    
    ## @brief Update a component in DB
    # @param datas dict : If None use instance attributes to update de DB
    # @return True if success
    # @todo better error handling
    def update(self, datas = None):
        datas = self.datas(internal=False) if datas is None else datas
        upd_datas = self.prepare_datas(datas, complete = False, allow_internal = False)
        filters = [self._id_filter()]
        rel_filters = []
        ret = self._datasource.update(self.__class__, filters, rel_filters, upd_datas)
        if ret == 1:
            return True
        else:
            #ERROR HANDLING
            return False
    
    ## @brief Delete a component
    # @return True if success
    # @todo better error handling
    def delete(self):
        filters = [self._id_filter()]
        rel_filters = []
        ret = self._datasource.delete(self.__class__, filters, rel_filters)
        if ret == 1:
            return True
        else:
            #ERROR HANDLING
            return False

    ## @brief Check that datas are valid for this type
    # @param datas dict : key == field name value are field values
    # @param complete bool : if True expect that datas provide values for all non internal fields
    # @param allow_internal bool : if True don't raise an error if a field is internal
    # @return Checked datas
    # @throw LeApiDataCheckError if errors reported during check
    @classmethod
    def check_datas_value(cls, datas, complete = False, allow_internal = True):
        err_l = [] #Stores errors
        correct = [] #Valid fields name
        mandatory = [] #mandatory fields name
        for fname, ftt in cls.fieldtypes().items():
            if allow_internal or not ftt.is_internal():
                correct.append(fname)
                if complete and not hasattr(ftt, 'default'):
                    mandatory.append(fname)
        mandatory = set(mandatory)
        correct = set(correct)
        provided = set(datas.keys())

        #searching unknow fields
        print("provided", provided, "correct", correct)
        unknown = provided - correct
        for u_f in unknown:
            #here we can check if the field is unknown or rejected because it is internal
            err_l.append(AttributeError("Unknown or unauthorized field '%s'"%u_f))
        #searching missings fields
        missings = mandatory - provided
        for miss_field in missings:
            err_l.append(AttributeError("The data for field '%s' is missing"%miss_field))
        #Checks datas
        checked_datas = dict()
        for name, value in [ (name, value) for name, value in datas.items() if name in correct ]:
            checked_datas[name], err = cls.fieldtypes()[name].check_data_value(value)
            if err:
                err_l.append(err)

        if len(err_l) > 0:
            raise LeApiDataCheckError("Error while checking datas", err_l)
        return checked_datas

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
    
    ## @brief Given filters delete components
    # @param filters list : list of string of query filters (or tuple (FIELD, OPERATOR, VALUE) ) see @ref leobject_filters
    # @return the number of deleted components
    # @todo Check for Abstract calls (with cls == LeCrud)
    @classmethod
    def delete_multi(cls, filters):
        filters, rel_filters = cls._prepare_filters(filters)
        return cls._datasource.delete(cls, filters, rel_filters)
    
    ## @brief Insert a new component
    # @param datas dict : The value of object we want to insert
    # @return A new id if success else False
    @classmethod
    def insert(cls, datas):
        insert_datas = self.prepare_datas(datas, complete = True, allow_internal = False)
        return cls._datasource.insert(cls, insert_datas)
    
    ## @brief Check and prepare datas
    # 
    # @warning when complete = False we are not able to make construct_datas() and _check_data_consistency()
    # 
    # @param datas dict : {fieldname : fieldvalue, ...}
    # @param complete bool : If True you MUST give all the datas
    # @param allow_internal : Wether or not interal fields are expected in datas
    # @return Datas ready for use
    @classmethod
    def prepare_datas(cls, datas, complete = False, allow_internal = True):
        if not complete:
            warnings.warn("Actual implementation can make datas construction and consitency checks fails when datas are not complete")
        ret_dats = self.check_datas_value(cls, datas, complete, allow_internal)
        ret_datas = self._construct_datas(cls, ret_datas)
        ret_datas = self._check_data_consistency(cls, ret_datas)
        return ret_datas

    #-###################-#
    #   Private methods   #
    #-###################-#
    
    ## @brief Build a filter to select an object with a specific ID
    # @warning assert that the uid is not composed with multiple fieldtypes
    # @return A filter of the form tuple(UID, '=', self.UID)
    def _id_filter(self):
        id_name = self._uid_fieldtype.keys()[0]
        return ( id_name, '=', getattr(self, id_name) )

    ## @brief Construct datas values
    #
    # @warning assert that datas is complete
    #
    # @param datas dict : Datas that have been returned by LeCrud.check_datas_value() methods
    # @return A new dict of datas
    # @todo Decide wether or not the datas are modifed inplace or returned in a new dict (second solution for the moment)
    @classmethod
    def _construct_datas(cls, datas):
        res_datas = dict()
        for fname, ftype in cls.fieldtypes().items():
            if fname in datas:
                res_datas[fname] = ftype.construct_data(datas)
        return res_datas
    ## @brief Check datas consistency
    # 
    # @warning assert that datas is complete
    #
    # @param datas dict : Datas that have been returned by LeCrud._construct_datas() method
    # @throw LeApiDataCheckError if fails
    @classmethod
    def _check_datas_consistency(cls, datas):
        err_l = []
        for fname, ftype in cls.fieldtypes().items():
            ret = ftype.check_data_consistency(datas)
            if isinstance(ret, Exception):
                err_l.append(ret)

        if len(err_l) > 0:
            raise LeApiDataCheckError("Datas consistency checks fails", err_l)
        

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
    
    ## @brief Check if a field is relational or not
    # @param field str : the field to test
    # @return True if the field is relational else False
    @staticmethod
    def _field_is_relational(field):
        return field.startswith('superior.') or field.startswith('subordinate')



