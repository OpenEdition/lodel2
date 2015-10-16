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
    # @param query_filters list : list of string of query filters (or tuple (FIELD, OPERATOR, VALUE) )
    # @param field_list list|None : list of string representing fields
    # @param typename str : The name of the LeType we want
    # @param classname str : The name of the LeClass we want
    # @return responses ({string:*}): a list of dict with field:value
    def get(self, query_filters, field_list = None, typename = None, classname = None):
        filters = list()
        for query in query_filters:
            if len(query) == 3 and not isinstance(query, str):
                filters.append(tuple(query))
            else:
                filters.append(self._split_filter(query))
        #Now filters is a list of tuple (FIELD, OPERATOR, VALUE
        
        #Fetching LeType
        if typename is None:
            letype = None
        else:
            letype = leobject.lefactory.LeFactory.leobj_from_name(typename)

        #Fetching LeClass
        if classname is None:
            leclass = None
        else:
            leclass = leobject.lefactory.LeFactory.leobj_from_name(classname)
            if not emclass:
                raise LeObjectQueryError("No such EmClass : '%s'"%classname)

        #Checking field_list
        if field_list is None:
            if not (letype is None):
                flist = letype._fields
            elif not (leclass is None):
                flist = leclass._fieldtypes.keys()
            else:
                flist = EditorialModel.classtype.common_fields.keys()
        else:
            LeFactory._check_fields(letype, leclass, field_list)
        
        #Checking relational filters (for the moment fields like superior.NATURE)
        relational_filters = [ LeFactory._nature_from_relational_field(field), operator, value for field, operator, value in filters if LeFactory._field_is_relational(field)]
        filters = [f for f in filters if not self._field_is_relational(f[0])]
        #Checking the rest of the fields
        LeFactory._check_fields(letype, leclass, [ f[0] for f in filters ])

        return self._datasource.get(emclass, emtype, filters, relational_filters)

    ## @brief Check if a fieldname is valid
    # @param letype LeType|None : The concerned type (or None)
    # @param leclass LeClass|None : The concerned class (or None)
    # @param fields list : List of string representing fields
    # @throw LeObjectQueryError if their is some problems
    # @throw AttributeError if letype is not from the leclass class
    @staticmethod
    def _check_fields(letype, leclass, fields):
        #Checking that fields in the query_filters are correct
        if letype is None and leclass is None:
            #Only fields from the object table are allowed
            for field in fields:
                if field not in EditorialModel.classtype.common_fields.keys():
                    raise LeObjectQueryError("Not typename and no classname given, but the field %s is not in the common_fields list"%field)
        else:
            if letype is None:
                field_l = leclass._fieldtypes.keys()
            else:
                if not (leclass is None):
                    if letype._leclass != leclass:
                        raise AttributeError("The EmType %s is not a specialisation of the EmClass %s"%(typename, classname))
                field_l = letype._fields
            #Checks that fields are in this type
            for field in fields:
                if field not in fields_l:
                    raise LeObjectQueryError("No field named '%s' in '%s'"%(field, typename))
        pass

    ## @brief Check if a field is relational or not
    # @param field str : the field to test
    # @return True if the field is relational else False
    @staticmethod
    def _field_is_relational(field):
        return field.startwith('superior.')
    
    ## @brief Check that a relational field is valid
    # @param fields str : a relational field
    # @return a nature
    @staticmethod
    def _nature_from_relational_field(field):
        spl = field.split('.')
        if len(spl) != 2:
            raise LeObjectQueryError("The relationalfield '%s' is not valid"%field)
        nature = spl[-1]
        if nature not in EditorialModel.classtypes.EmNature.getall():
            raise LeObjectQueryError("'%s' is not a valid nature in the field %s"%(nature, field))
        return nature

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
