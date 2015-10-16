#-*- coding: utf-8 -*-

## @package EditorialModel::leobject::leobject
# @brief Main class to handle objects defined by the types of an Editorial Model
# an instance of these objects is pedantically called LeObject !

import re
from EditorialModel.types import EmType

class _LeObject(object):
    
    ## @brief The editorial model
    _model = None
    ## @brief The datasource
    _datasource = None

    _query_re = None
    _query_operators = ['=', '<=', '>=', '!=', '<', '>', ' in ', ' not in ']
    
    ## @brief Instantiate with a Model and a DataSource
    # @param **kwargs dict : datas usefull to instanciate a _LeObject
    def __init__(self, **kwargs):
        raise NotImplementedError("Abstract constructor")

    ## @brief create a new LeObject
    # @param data dict: a dictionnary of field:value to save
    # @return lodel_id int: new lodel_id of the newly created LeObject
    def insert(self, data):
        try:
            checked_data = self._check_data(data)
            lodel_id = self.datasource.insert(checked_data)
        except:
            raise
        return lodel_id

    ## @brief update an existing LeObject
    # @param lodel_id int | (int): lodel_id of the object(s) where to apply changes
    # @param data dict: dictionnary of field:value to save
    # @param update_filters string | (string): list of string of update filters
    # @return okay bool: True on success, it will raise on failure
    def update(self, lodel_id, data, update_filters=None):
        if not lodel_id:
            lodel_id = ()
        elif isinstance(lodel_id, int):
            lodel_id = (lodel_id)

        try:
            checked_data = self._check_data(data)
            datasource_filters = self._prepare_filters(update_filters)
            okay = self.datasource.update(lodel_id, checked_data, datasource_filters)
        except:
            raise
        return okay

    ## @brief delete an existing LeObject
    # @param lodel_id int | (int): lodel_id of the object(s) to delete
    # @param delete_filters string | (string): list of string of delete filters
    # @return okay bool: True on success, it will raise on failure
    def delete(self, lodel_id, delete_filters=None):
        if not lodel_id:
            lodel_id = ()
        elif isinstance(lodel_id, int):
            lodel_id = (lodel_id)

        try:
            datasource_filters = self._prepare_filters(delete_filters)
            okay = self.datasource.delete(lodel_id, datasource_filters)
        except:
            raise
        return okay

    ## @brief make a search to retrieve a collection of LeObject
    # @param 
    # @param query_filters list : list of string of query filters (or tuple (FIELD, OPERATOR, VALUE) )
    # @return responses ({string:*}): a list of dict with field:value
    def get(self, query_filters, typename = None, classname = None):
        filters = list()
        for query in query_filters:
            if len(query) == 3 and not isinstance(query, str):
                filters.append(tuple(query))
            else:
                filters.append(self._split_filter(query))
        #Now filters is a list of tuple (FIELD, OPERATOR, VALUE
        #Begining to check the filters
        
        #Fetching EmType
        if typename is None:
            emtype = None
        else:
            emtype = self._model.component_from_name(typename, 'EmType')
            if not emtype:
                raise LeObjectQueryError("No such EmType : '%s'"%typename)
        #Fetching EmClass
        if classname is None:
            emclass = None
        else:
            emclass = self._model.component_from_name(classname, 'EmClass')
            if not emclass:
                raise LeObjectQueryError("No such EmClass : '%s'"%classname)

        #Checking that fields in the query_filters are correct
        if emtype is None and emclass is None:
            #Only fields from the object table are allowed
            for field,_,_ in filters:
                if field not in EditorialModel.classtype.common_fields:
                    raise LeObjectQueryError("Not typename and no classname given, but the field %s is not in the common_fields list"%field)
        else:
            if emtype is None:
                field_l = emclass.fields()
            else:
                if not (emclass is None):
                    if emtype.em_class != emclass:
                        raise LeObjectQueryError("The EmType %s is not a specialisation of the EmClass %s"%(typename, classname))
                else:
                    #Set emclass (to query the db ?
                    emclass = emtype.em_class
                field_l = emtype.fields()
            #Checks that fields are in this type
            for field,_,_ in filters:
                if field not in [ f.name for f in fields_l ]:
                    raise LeObjectQueryError("No field named '%s' in '%s'"%(field, typename))

        return self._datasource.get(emclass, emtype, filters)

    ## @brief check if data dict fits with the model
    # @param data dict: dictionnary of field:value to check
    # @return checked_data ({string:*}): a list of dict with field:value
    # @todo implent !
    def _check_data(self, data):
        checked_data = data
        return checked_data
    
    ## @brief Check and split a query filter
    # @note The query_filter format is "FIELD OPERATOR VALUE"
    # @param query_filter str : A query_filter string
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
        cls._query_re = re.compile('^\s*(?P<field>(superior\.)?[a-z_][a-z0-9\-_]*)\s*'+op_re_piece+'\s*(?P<value>[^<>=!].*)\s*$', flags=re.IGNORECASE)
        pass

class LeObjectError(Exception):
    pass

class LeObjectQueryError(LeObjectError):
    pass
