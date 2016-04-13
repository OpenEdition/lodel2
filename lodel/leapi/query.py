#-*- coding: utf-8 -*-

import re
from .leobject import LeObject, LeApiErrors, LeApiDataCheckError
from lodel.plugin.hooks import LodelHook

class LeQueryError(Exception):
    pass

class LeQuery(object):
    
    ##@brief Hookname preffix
    _hook_prefix = None
    ##@brief arguments for the LeObject.check_data_value()
    _data_check_args = { 'complete': False, 'allow_internal': False }

    ##@brief Abstract constructor
    # @param target_class LeObject : class of object the query is about
    def __init__(self, target_class):
        if hook_prefix is None:
            raise NotImplementedError("Asbtract class")
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
    def execute(self, datasource, **datas):
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
                        ' in ',
                        ' not in ',
                        ' like ',
                        ' not like ']

    ##@brief Abtract constructor for queries with filter
    # @param target_class LeObject : class of object the query is about
    # @param query_filters list : list of string of query filters (or tuple 
    #(FIELD, OPERATOR, VALUE) )
    def __init__(self, target_class, query_filter):
        super().__init__(target_class)
        ##@brief The query filter
        self.__query_filter = None
        self.set_qeury_filter(query_filter)
    
    ##@brief Set the query filter for a query
    def set_query_filter(self, query_filter):
        #
        #   Query filter check & prepare should be done here
        #
        self.__query_filter = query_filter

##@brief A query for insert a new object
class LeInsertQuery(LeQuery):
    
    _hook_prefix = 'leapi_insert_'
    _data_check_args = { 'complete': True, 'allow_internal': False }

    def __init__(self, target_class):
        super().__init__(target_class)
    
    ## @brief Implements an insert query operations
    # @param **datas : datas to be inserted
    def __query(self, datasource, **datas):
        pass

##@brief A query to update datas for a given object
class LeUpdateQuery(LeFilteredQuery):
    
    _hook_prefix = 'leapi_update_'
    _data_check_args = { 'complete': True, 'allow_internal': False }

    def __init__(self, target_class, query_filter):
        super().__init__(target_class, query_filter)
    
    ##@brief Implements an update query
    # @param **datas : datas to update
    def __query(self, datasource, **datas):
        pass

##@brief A query to delete an object
class LeDeleteQuery(LeFilteredQuery):
    
    _hook_prefix = 'leapi_delete_'

    def __init__(self, target_class, query_filter):
        super().__init__(target_class, query_filter)

    ## @brief Execute the delete query
    def execute(self, datasource):
        super().execute()
    
    ##@brief Implements delete query operations
    def __query(self, datasource):
        pass

class LeGetQuery(LeFilteredQuery):
    
    _hook_prefix = 'leapi_get_'

    ##@brief Instanciate a new get query
    # @param target_class LeObject : class of object the query is about
    # @param query_filters list : list of string of query filters (or tuple 
    #(FIELD, OPERATOR, VALUE) )
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
            pass
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

