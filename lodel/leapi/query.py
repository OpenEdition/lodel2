#-*- coding: utf-8 -*-

import re
from .leobject import LeObject, LeApiErrors, LeApiDataCheckError
from lodel.plugin.hooks import LodelHook

class LeQueryError(Exception):
    ##@brief Instanciate a new exceptions handling multiple exceptions
    # @param msg str : Exception message
    # @param exceptions dict : A list of data check Exception with concerned field (or stuff) as key
    def __init__(self, msg = "Unknow error", exceptions = None):
        self._msg = msg
        self._exceptions = dict() if exceptions is None else exceptions

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        msg = self._msg
        for_iter = self._exceptions.items() if isinstance(self._exceptions, dict) else enumerate(self.__exceptions)
        for obj, expt in for_iter:
            msg += "\n\t{expt_obj} : ({expt_name}) {expt_msg}; ".format(
                    expt_obj = obj,
                    expt_name=expt.__class__.__name__,
                    expt_msg=str(expt)
            )
        return msg

class LeQuery(object):
    
    ##@brief Hookname prefix
    _hook_prefix = None
    ##@brief arguments for the LeObject.check_data_value()
    _data_check_args = { 'complete': False, 'allow_internal': False }

    ##@brief Abstract constructor
    # @param target_class LeObject : class of object the query is about
    def __init__(self, target_class):
        if hook_prefix is None:
            raise NotImplementedError("Abstract class")
        if not issubclass(target_class, LeObject):
            raise TypeError("target class has to be a child class of LeObject")
        self.__target_class = target_class
    
    ##@brief Execute a query and return the result
    # @param **datas
    # @return the query result
    # @see LeQuery.__query()
    #
    # @note maybe the datasource in not an argument but should be determined
    #elsewhere
    def execute(self, datasource, **datas = None):
        if len(datas) > 0:
            self.__target_class.check_datas_value(datas, **self._data_check_args)
            self.__target_class.prepare_datas() #not yet implemented
        if self._hook_prefix is None:
            raise NotImplementedError("Abstract method")
        LodelHook.call_hook(    self._hook_prefix+'_pre',
                                self.__target_class,
                                datas)
        ret = self.__query(datasource, **datas)
        ret = LodelHook.call_hook(  self._hook_prefix+'_post',
                                    self.__target_class,
                                    ret)
        return ret
    
    ##@brief Childs classes implements this method to execute the query
    # @param **datas
    # @return query result
    def __query(self, **datas):
        raise NotImplementedError("Asbtract method")

class LeFilteredQuery(LeQuery):
    
    ##@brief The available operators used in query definitions
    query_operators = [
                        '=',
                        '<=',
                        '>=',
                        '!=',
                        '<',
                        '>',
                        'in',
                        'not in',
                        'like',
                        'not like']

    ##@brief Abtract constructor for queries with filter
    # @param target_class LeObject : class of object the query is about
    # @param query_filters list : with a tuple (only one filter) or a list of tuple
    #   or a dict: {OP,list(filters)} with OP = 'OR' or 'AND
    #   For tuple (FIELD,OPERATOR,VALUE)
    def __init__(self, target_class, query_filter):
        super().__init__(target_class)
        ##@brief The query filter
        self.__query_filter = None
        self.set_query_filter(query_filter)
    
    ##@brief Set the query filter for a query
    def set_query_filter(self, query_filter):
        #
        #   Query filter check & prepare 
        #   query_filters can be a tuple (only one filter), a list of tuple
        #   or a dict: {OP,list(filters)} with OP = 'OR' or 'AND
        #   For tuple (FIELD,OPERATOR,VALUE)
        #   FIELD has to be in the field_names list of target class
        #   OPERATOR in query_operator attribute
        #   VALUE has to be a correct value for FIELD

        fieldnames = self.__target_class.fieldnames()
        # Recursive method which checks filters
        def check_tuple(tupl, fieldnames, target_class):
            if isinstance(tupl, tuple):
                if tupl[0] not in fieldnames:
                    return False
                if tupl[1] not in self.query_operators:
                    return False
                if not isinstance(tupl[2], target_class.datahandler(tupl[0])):
                    return False
                return True
            elif isinstance(tupl,dict):
                return check_tuple(tupl[1])
            elif isinstance(tupl,list):
                for tup in tupl:
                    return check_tuple(tup)
            else: 
                raise TypeError("Wrong filters for query")

        check_ok=check_tuple(query_filter, fieldnames, self.__target_class)
        if check_ok:            
            self.__query_filter = query_filter
            
		def execute(self, datasource, **datas = None):
			super().execute(datasource, **datas)

##@brief A query to insert a new object
class LeInsertQuery(LeQuery):
    
    _hook_prefix = 'leapi_insert_'
    _data_check_args = { 'complete': True, 'allow_internal': False }

    def __init__(self, target_class):
        super().__init__(target_class)
    
    ## @brief Implements an insert query operation, with only one insertion
    # @param **datas : datas to be inserted
    def __query(self, datasource, **datas):
        nb_inserted = datasource.insert(self.__target_class,**datas)
        if nb_inserted < 0:
            raise LeQueryError("Insertion error")
        return nb_inserted
    ## @brief Implements an insert query operation, with multiple insertions
    # @param datas : list of **datas to be inserted
    def __query(self, datasource, datas):
        nb_inserted = datasource.insert_multi(self.__target_class,datas_list)
        if nb_inserted < 0:
            raise LeQueryError("Multiple insertions error")
        return nb_inserted
    ## @brief Execute the insert query
    def execute(self, datasource, **datas):
        super().execute(datasource, **datas)
        
##@brief A query to update datas for a given object
class LeUpdateQuery(LeFilteredQuery):
    
    _hook_prefix = 'leapi_update_'
    _data_check_args = { 'complete': True, 'allow_internal': False }

    def __init__(self, target_class, query_filter):
        super().__init__(target_class, query_filter)
    
    ##@brief Implements an update query
    # @param **datas : datas to update
    # @returns the number of updated items
    # @exception when the number of updated items is not as expected
    def __query(self, datasource, **datas):
        # select _uid corresponding to query_filter
        l_uids=datasource.select(self.__target_class,list(self.__target_class.getuid()),query_filter,None, None, None, None, 0, False)
        # list of dict l_uids : _uid(s) of the objects to be updated, corresponding datas
        nb_updated = datasource.update(self.__target_class,l_uids, **datas)
        if (nb_updated != len(l_uids):
            raise LeQueryError("Number of updated items: %d is not as expected: %d " % (nb_updated, len(l_uids)))
        return nb_updated
    
    ## @brief Execute the update query
    def execute(self, datasource, **datas):
        super().execute(datasource, **datas)

##@brief A query to delete an object
class LeDeleteQuery(LeFilteredQuery):
    
    _hook_prefix = 'leapi_delete_'

    def __init__(self, target_class, query_filter):
        super().__init__(target_class, query_filter)

    ## @brief Execute the delete query
    def execute(self, datasource):
        super().execute()
    
    ##@brief Implements delete query operations
    # @returns the number of deleted items
    # @exception when the number of deleted items is not as expected
    def __query(self, datasource):
        # select _uid corresponding to query_filter
        l_uids=datasource.select(self.__target_class,list(self.__target_class.getuid()),query_filter,None, None, None, None, 0, False)
        # list of dict l_uids : _uid(s) of the objects to be deleted
        nb_deleted = datasource.update(self.__target_class,l_uids, **datas)
        if (nb_deleted != len(l_uids):
            raise LeQueryError("Number of deleted items %d is not as expected %d " % (nb_deleted, len(l_uids)))
        return nb_deleted

class LeGetQuery(LeFilteredQuery):
    
    _hook_prefix = 'leapi_get_'

    ##@brief Instanciate a new get query
    # @param target_class LeObject : class of object the query is about
    # @param query_filters dict : {OP, list of query filters }
    #        or tuple (FIELD, OPERATOR, VALUE) )
    # @param field_list list|None : list of string representing fields see @ref leobject_filters
    # @param order list : A list of field names or tuple (FIELDNAME, [ASC | DESC])
    # @param group list : A list of field names or tuple (FIELDNAME, [ASC | DESC])
    # @param limit int : The maximum number of returned results
    # @param offset int : offset
    def __init__(self, target_class, query_filter, **kwargs):
        super().__init__(target_class, query_filter)
        
        ##@brief The fields to get
        self.__field_list = None
        ##@brief An equivalent to the SQL ORDER BY
        self.__order = None
        ##@brief An equivalent to the SQL GROUP BY
        self.__group = None
        ##@brief An equivalent to the SQL LIMIT x
        self.__limit = None
        ##@brief An equivalent to the SQL LIMIT x, OFFSET
        self.__offset = 0
        
        # Checking kwargs and assigning default values if there is some
        for argname in kwargs:
            if argname not in ('order', 'group', 'limit', 'offset'):
                raise TypeError("Unexpected argument '%s'" % argname)

        if 'field_list' not in kwargs:
            #field_list = target_class.get_field_list
            field_list = target_class.fieldnames()
        else:
            #target_class.check_fields(kwargs['field_list'])
            field_list = kwargs['field_list']
        if 'order' in kwargs:
            #check kwargs['order']
            self.__order = kwargs['order']
        if 'group' in kwargs:
            #check kwargs['group']
            self.__group = kwargs['group']
        if 'limit' in kwargs:
            try:
                self.__limit = int(kwargs[limit])
                if self.__limit <= 0:
                    raise ValueError()
            except ValueError:
                raise ValueError("limit argument expected to be an interger > 0")
        if 'offset' in kwargs:
            try:
                self.__offset = int(kwargs['offset'])
                if self.__offset < 0:
                    raise ValueError()
            except ValueError:
                raise ValueError("offset argument expected to be an integer >= 0")
    
    ##@brief Execute the get query
    def execute(self, datasource):
        super().execute(datasource)

    ##@brief Implements select query operations
    # @returns a list containing the item(s)

    def __query(self, datasource):
        # select datas corresponding to query_filter
        l_datas=datasource.select(self.__target_class,list(self.field_list),self.query_filter,None, self.__order, self.__group, self.__limit, self.offset, False)
        return l_datas
        


