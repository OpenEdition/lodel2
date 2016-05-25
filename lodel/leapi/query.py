#-*- coding: utf-8 -*-

import re
from .leobject import LeObject, LeApiErrors, LeApiDataCheckError
from lodel.plugin.hooks import LodelHook
from lodel import logger

class LeQueryError(Exception):
    ##@brief Instanciate a new exceptions handling multiple exceptions
    #@param msg str : Exception message
    #@param exceptions dict : A list of data check Exception with concerned
    # field (or stuff) as key
    def __init__(self, msg = "Unknow error", exceptions = None):
        self._msg = msg
        self._exceptions = dict() if exceptions is None else exceptions

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        msg = self._msg
        if isinstance(self._exceptions, dict):
            for_iter = self._exceptions.items()
        else:
            for_iter = enumerate(self.__exceptions)
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
        if self._hook_prefix is None:
            raise NotImplementedError("Abstract class")
        if not issubclass(target_class, LeObject):
            raise TypeError("target class has to be a child class of LeObject")
        self._target_class = target_class
    
    ##@brief Execute a query and return the result
    # @param **datas
    # @return the query result
    # @see LeQuery.__query()
    #
    # @note maybe the datasource in not an argument but should be determined
    #elsewhere
    def execute(self, datasource, datas = None):
        if len(datas) > 0:
            self._target_class.check_datas_value(
                                                    datas,
                                                    **self._data_check_args)
            self._target_class.prepare_datas() #not yet implemented
        if self._hook_prefix is None:
            raise NotImplementedError("Abstract method")
        LodelHook.call_hook(    self._hook_prefix+'_pre',
                                self._target_class,
                                datas)
        ret = self.__query(datasource, **datas)
        ret = LodelHook.call_hook(  self._hook_prefix+'_post',
                                    self._target_class,
                                    ret)
        return ret
    
    ##@brief Childs classes implements this method to execute the query
    # @param **datas
    # @return query result
    def __query(self, **datas):
        raise NotImplementedError("Asbtract method")
    
    ##@return a dict with query infos
    def dump_infos(self):
        return {'target_class': self._target_class}

    def __repr__(self):
        ret = "<{classname} target={target_class}>"
        return ret.format(
                            classname=self.__class__.__name__,
                            target_class = self._target_class)
        

class LeFilteredQuery(LeQuery):
    
    ##@brief The available operators used in query definitions
    _query_operators = [
                        ' = ',
                        ' <= ',
                        ' >= ',
                        ' != ',
                        ' < ',
                        ' > ',
                        ' in ',
                        ' not in ',
                        ' like ',
                        ' not like ']
    
    ##@brief Regular expression to process filters
    _query_re = None

    ##@brief Abtract constructor for queries with filter
    # @param target_class LeObject : class of object the query is about
    # @param query_filters list : with a tuple (only one filter) or a list of tuple
    #   or a dict: {OP,list(filters)} with OP = 'OR' or 'AND
    #   For tuple (FIELD,OPERATOR,VALUE)
    def __init__(self, target_class, query_filters = None):
        super().__init__(target_class)
        ##@brief The query filter tuple(std_filter, relational_filters)
        self.__query_filter = None
        self.set_query_filter(query_filters)
    
    ##@brief Add filter(s) to the query
    #@param query_filter list|tuple|str : A single filter or a list of filters
    #@see LeFilteredQuery._prepare_filters()
    def set_query_filter(self, query_filter):
        if isinstance(query_filter, str):
            query_filter = [query_filter]
        self.__query_filter = self._prepare_filters(query_filter)

    def dump_infos(self):
        ret = super().dump_infos()
        ret['query_filter'] = self.__query_filter
        return ret

    def __repr__(self):
        ret = "<{classname} target={target_class} query_filter={query_filter}>"
        return ret.format(
                            classname=self.__class__.__name__,
                            query_filter = self.__query_filter,
                            target_class = self._target_class)
    ## @brief Prepare filters for datasource
    # 
    #A filter can be a string or a tuple with len = 3.
    #
    #This method divide filters in two categories :
    #
    #@par Simple filters
    #
    #Those filters concerns fields that represent object values (a title,
    #the content, etc.) They are composed of three elements : FIELDNAME OP
    # VALUE . Where :
    #- FIELDNAME is the name of the field
    #- OP is one of the authorized comparison operands ( see 
    #@ref LeFilteredQuery.query_operators )
    #- VALUE is... a value
    #
    #@par Relational filters
    #
    #Those filters concerns on reference fields ( see the corresponding
    #abstract datahandler @ref lodel.leapi.datahandlers.base_classes.Reference)
    #The filter as quite the same composition than simple filters :
    # FIELDNAME[.REF_FIELD] OP VALUE . Where :
    #- FIELDNAME is the name of the reference field
    #- REF_FIELD is an optionnal addon to the base field. It indicate on wich
    #field of the referenced object the comparison as to be done. If no
    #REF_FIELD is indicated the comparison will be done on identifier.
    #
    #@param cls
    #@param filters_l list : This list of str or tuple (or both)
    #@return a tuple(FILTERS, RELATIONNAL_FILTERS
    #@todo move this doc in another place (a dedicated page ?)
    def _prepare_filters(self, filters_l):
        filters = list()
        res_filters = list()
        rel_filters = list()
        err_l = dict()
        #Splitting in tuple if necessary
        for i,fil in enumerate(filters_l):
            if len(fil) == 3 and not isinstance(fil, str):
                filters.append(tuple(fil))
            else:
                try:
                    filters.append(self.split_filter(fil))
                except ValueError as e:
                    err_l["filter %d" % i] = e

        for field, operator, value in filters:
            err_key = "%s %s %s" % (field, operator, value) #to push in err_l
            # Spliting field name to be able to detect a relational field
            field_spl = field.split('.')
            if len(field_spl) == 2:
                field, ref_field = field_spl
            elif len(field_spl) == 1:
                ref_field = None
            else:
                err_l[field] = NameError(   "'%s' is not a valid relational \
field name" % fieldname)
                continue   
            # Checking field against target_class
            ret = self.__check_field(self._target_class, field)
            if isinstance(ret, Exception):
                err_l[field] = ret
                continue
            field_datahandler = self._target_class.field(field)
            if ref_field is not None and not field_datahandler.is_reference():
                # inconsistency
                err_l[field] = NameError(   "The field '%s' in %s is not \
a relational field, but %s.%s was present in the filter"
                                            % ( field,
                                                self._target_class.__name__,
                                                field,
                                                ref_field))
            if field_datahandler.is_reference():
                #Relationnal field
                if ref_field is None:
                    # ref_field default value
                    ref_uid = set([ lc._uid for lc in field_datahandler.linked_classes])
                    if len(ref_uid) == 1:
                        ref_field = ref_uid[0]
                    else:
                        if len(ref_uid) > 1:
                            err_l[err_key] = RuntimeError("The referenced classes are identified by fields with different name. Unable to determine wich field to use for the reference")
                        else:
                            err_l[err_key] = RuntimeError("Unknow error when trying to determine wich field to use for the relational filter")
                        continue
                # Prepare relational field
                ret = self._prepare_relational_fields(field, ref_field)
                if isinstance(ret, Exception):
                    err_l[err_key] = ret
                    continue
                else:
                    rel_filters.append((ret, operator, value))
            else:
                res_filters.append((field,operator, value))
        
        if len(err_l) > 0:
            raise LeApiDataCheckError(
                                        "Error while preparing filters : ",
                                        err_l)
        return (res_filters, rel_filters)
    
    ## @brief Prepare & check relational field
    #
    # The result is a tuple with (field, ref_field, concerned_classes), with :
    # - field the target_class field name
    # - ref_field the concerned_classes field names
    # - concerned_classes a set of concerned LeObject classes
    # @param field str : The target_class field name
    # @param ref_field str : The referenced class field name
    # @return a tuple(field, concerned_classes, ref_field) or an Exception class instance
    def _prepare_relational_fields(self,field, ref_field):
        field_dh = self._target_class.field(field)
        concerned_classes = []
        linked_classes = [] if field_dh.linked_classes is None else field_dh.linked_classes
        for l_class in linked_classes:
            try:
                l_class.field(ref_field)
                concerned_classes.append(l_class)
            except KeyError:
                pass
        if len(concerned_classes) > 0:
            return (field, ref_field, concerned_classes)
        else:
            return ValueError("None of the linked class of field %s has a field named '%s'" % (field, ref_field))

    ## @brief Check and split a query filter
    # @note The query_filter format is "FIELD OPERATOR VALUE"
    # @param query_filter str : A query_filter string
    # @param cls
    # @return a tuple (FIELD, OPERATOR, VALUE)
    @classmethod
    def split_filter(cls, query_filter):
        if cls._query_re is None:
            cls.__compile_query_re()
        matches = cls._query_re.match(query_filter)
        if not matches:
            raise ValueError("The query_filter '%s' seems to be invalid"%query_filter)
        result = (matches.group('field'), re.sub(r'\s', ' ', matches.group('operator'), count=0), matches.group('value').strip())
        result = [r.strip() for r in result]
        for r in result:
            if len(r) == 0:
                raise ValueError("The query_filter '%s' seems to be invalid"%query_filter)
        return result

    ## @brief Compile the regex for query_filter processing
    # @note Set _LeObject._query_re
    @classmethod
    def __compile_query_re(cls):
        op_re_piece = '(?P<operator>(%s)'%cls._query_operators[0].replace(' ', '\s')
        for operator in cls._query_operators[1:]:
            op_re_piece += '|(%s)'%operator.replace(' ', '\s')
        op_re_piece += ')'
        cls._query_re = re.compile('^\s*(?P<field>([a-z_][a-z0-9\-_]*\.)?[a-z_][a-z0-9\-_]*)\s*'+op_re_piece+'\s*(?P<value>.*)\s*$', flags=re.IGNORECASE)
        pass

    @classmethod
    def __check_field(cls, target_class, fieldname):
        try:
            target_class.field(fieldname)
        except NameError:
            tc_name = target_class.__name__
            return ValueError("No such field '%s' in %s" % (    fieldname,
                                                                tc_name))

    ##@brief Prepare a relational filter
    #
    #Relational filters are composed of a tuple like the simple filters
    #but the first element of this tuple is a tuple to :
    #
    #<code>( (FIELDNAME, {REF_CLASS: REF_FIELD}), OP, VALUE)</code>
    # Where :
    #- FIELDNAME is the field name is the target class
    #- the second element is a dict with :
    # - REF_CLASS as key. It's a LeObject child class
    # - REF_FIELD as value. The name of the referenced field in the REF_CLASS
    #
    #Visibly the REF_FIELD value of the dict will vary only when
    #no REF_FIELD is explicitly given in the filter string notation
    #and REF_CLASSES has differents uid
    #
    #@par String notation examples
    #<pre>contributeur IN (1,2,3,5)</pre> will be transformed into :
    #<pre>(
    #       (
    #           contributeur, 
    #           {
    #               auteur: 'lodel_id',
    #               traducteur: 'lodel_id'
    #           } 
    #       ),
    #       ' IN ',
    #       [ 1,2,3,5 ])</pre>
    #@todo move the documentation to another place
    #
    #@param fieldname str : The relational field name
    #@param ref_field str|None : The referenced field name (if None use
    #uniq identifiers as referenced field
    #@return a well formed relational filter tuple or an Exception instance
    @classmethod
    def __prepare_relational_fields(cls, fieldname, ref_field = None):
        datahandler = self._target_class.field(fieldname)
        # now we are going to fetch the referenced class to see if the
        # reference field is valid
        ref_classes = datahandler.linked_classes
        ref_dict = dict()
        if ref_field is None:
            for ref_class in ref_classes:
                ref_dict[ref_class] = ref_class.uid_fieldname
        else:
            for ref_class in ref_classes:
                if ref_field in ref_class.fieldnames(True):
                    ref_dict[ref_class] = ref_field
                else:
                    logger.debug("Warning the class %s is not considered in \
the relational filter %s" % ref_class.__name__)
        if len(ref_dict) == 0:
            return NameError(   "No field named '%s' in referenced objects"
                                % ref_field)
        return ( (fieldname, ref_dict), op, value)
 

##@brief A query to insert a new object
class LeInsertQuery(LeQuery):
    
    _hook_prefix = 'leapi_insert_'
    _data_check_args = { 'complete': True, 'allow_internal': False }

    def __init__(self, target_class):
        super().__init__(target_class)
    
    ## @brief Implements an insert query operation, with only one insertion
    # @param **datas : datas to be inserted
    def __query(self, datasource, **datas):
        nb_inserted = datasource.insert(self._target_class,**datas)
        if nb_inserted < 0:
            raise LeQueryError("Insertion error")
        return nb_inserted
    ## @brief Implements an insert query operation, with multiple insertions
    # @param datas : list of **datas to be inserted
    def __query(self, datasource, datas):
        nb_inserted = datasource.insert_multi(self._target_class,datas_list)
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
        l_uids=datasource.select(self._target_class,list(self._target_class.getuid()),query_filter,None, None, None, None, 0, False)
        # list of dict l_uids : _uid(s) of the objects to be updated, corresponding datas
        nb_updated = datasource.update(self._target_class,l_uids, **datas)
        if nb_updated != len(l_uids):
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
        l_uids=datasource.select(self._target_class,list(self._target_class.getuid()),query_filter,None, None, None, None, 0, False)
        # list of dict l_uids : _uid(s) of the objects to be deleted
        nb_deleted = datasource.update(self._target_class,l_uids, **datas)
        if nb_deleted != len(l_uids):
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
            self.__field_list = target_class.fieldnames(include_ro = True)
        else:
            #target_class.check_fields(kwargs['field_list'])
            self.__field_list = kwargs['field_list']
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
        l_datas=datasource.select(self._target_class,list(self.field_list),self.query_filter,None, self.__order, self.__group, self.__limit, self.offset, False)
        return l_datas
    
    ##@return a dict with query infos
    def dump_infos(self):
        ret = super().dump_infos()
        ret.update( {   'field_list' : self.__field_list,
                        'order' : self.__order,
                        'group' : self.__group,
                        'limit' : self.__limit,
                        'offset': self.__offset,
        })
        return ret

    def __repr__(self):
        ret = "<LeGetQuery target={target_class} filter={query_filter} field_list={field_list} order={order} group={group} limit={limit} offset={offset}>"
        return ret.format(**self.dump_infos())

