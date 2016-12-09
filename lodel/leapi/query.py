#-*- coding: utf-8 -*-

import re
import copy
import inspect
import warnings

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.leapi.exceptions': ['LeApiError', 'LeApiErrors', 
        'LeApiDataCheckError', 'LeApiDataCheckErrors', 'LeApiQueryError',
        'LeApiQueryErrors'],
    'lodel.plugin.hooks': ['LodelHook'],
    'lodel.logger': ['logger']})


##@todo check datas when running query
class LeQuery(object):
    
    ##@brief Hookname prefix
    _hook_prefix = None
    ##@brief arguments for the LeObject.check_data_value()
    _data_check_args = {'complete': False, 'allow_internal': False}

    ##@brief Abstract constructor
    # @param target_class LeObject : class of object the query is about
    def __init__(self, target_class):
        from .leobject import LeObject
        if self._hook_prefix is None:
            raise NotImplementedError("Abstract class")
        if not inspect.isclass(target_class) or \
           not issubclass(target_class, LeObject):
            raise TypeError("target class has to be a child class of LeObject but %s given"% target_class)
        self._target_class = target_class
        self._ro_datasource = target_class._ro_datasource
        self._rw_datasource = target_class._rw_datasource

    ##@brief Execute a query and return the result
    #@param **datas
    #@return the query result
    #@see LeQuery._query()
    #@todo check that the check_datas_value is not duplicated/useless
    def execute(self, datas):
        if not datas is None:
            self._target_class.check_datas_value(
                                                    datas,
                                                    **self._data_check_args)
            self._target_class.prepare_datas(datas) #not yet implemented
        if self._hook_prefix is None:
            raise NotImplementedError("Abstract method")
        LodelHook.call_hook(self._hook_prefix+'pre',
                                self._target_class,
                                datas)
        ret = self._query(datas=datas)
        ret = LodelHook.call_hook(self._hook_prefix+'post',
                                    self._target_class,
                                    ret)
        return ret

    ##@brief Childs classes implements this method to execute the query
    #@param **datas
    #@return query result
    def _query(self, **datas):
        raise NotImplementedError("Asbtract method")
    
    ##@return a dict with query infos
    def dump_infos(self):
        return {'target_class': self._target_class}

    def __repr__(self):
        ret = "<{classname} target={target_class}>"
        return ret.format(
                            classname=self.__class__.__name__,
                            target_class = self._target_class)

##@brief Abstract class handling query with filters
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
    #@param target_class LeObject : class of object the query is about
    #@param query_filters list : with a tuple (only one filter) or a list of
    # tuple or a dict: {OP,list(filters)} with OP = 'OR' or 'AND for tuple
    # (FIELD,OPERATOR,VALUE)
    def __init__(self, target_class, query_filters=None):
        super().__init__(target_class)
        ##@brief The query filter tuple(std_filter, relational_filters)
        self._query_filter = None
        ##@brief Stores potential subqueries (used when a query implies
        # more than one datasource.
        #
        # Subqueries are tuple(target_class_ref_field, LeGetQuery)
        self.subqueries = None
        query_filters = [] if query_filters is None else query_filters
        self.set_query_filter(query_filters)
        
    
    ##@brief Abstract FilteredQuery execution method
    #
    # This method takes care to execute subqueries before calling super execute
    def execute(self, datas=None):
        #copy originals filters
        orig_filters = copy.copy(self._query_filter)
        std_filters, rel_filters = self._query_filter

        for rfield, subq in self.subqueries:
            subq_res = subq.execute()
            std_filters.append(
                (rfield, ' in ', subq_res))
        self._query_filter = (std_filters, rel_filters)
        try:
            filters, rel_filters = self._query_filter
            res = super().execute(datas)
        except Exception as e:
            #restoring filters even if an exception is raised
            self.__query_filter = orig_filters

            raise e #reraise
        #restoring filters
        self._query_filter = orig_filters
        return res

    ##@brief Add filter(s) to the query
    #
    # This method is also able to slice query if different datasources are
    # implied in the request
    #
    #@param query_filter list|tuple|str : A single filter or a list of filters
    #@see LeFilteredQuery._prepare_filters()
    #@warning Does not support multiple UID
    def set_query_filter(self, query_filter):
        if isinstance(query_filter, str):
            query_filter = [query_filter]
        #Query filter prepration
        filters_orig, rel_filters = self._prepare_filters(query_filter)
        # Here we now that each relational filter concern only one datasource
        # thank's to _prepare_relational_fields

        #Multiple datasources detection
        self_ds_name = self._target_class._datasource_name
        result_rel_filters = list() # The filters that will stay in the query
        other_ds_filters = dict()
        for rfilter in rel_filters:
            (rfield, ref_dict), op, value = rfilter
            #rfield : the field in self._target_class
            tmp_rel_filter = dict() #designed to stores rel_field of same DS
            # First step : simplification
            # Trying to delete relational filters done on referenced class uid
            for tclass, tfield in copy.copy(ref_dict).items():
                #tclass : reference target class
                #tfield : referenced field from target class
                #
                #   !!!WARNING!!!
                # The line below brake multi UID support
                #
                if tfield == tclass.uid_fieldname()[0]:
                    #This relational filter can be simplified as
                    # ref_field, op, value
                    # Note : we will have to dedup filters_orig
                    filters_orig.append((rfield, op, value))
                    del(ref_dict[tclass])
            if len(ref_dict) == 0:
                continue
            #Determine what to do with other relational filters given
            # referenced class datasource
            #Remember : each class in a relational filter has the same
            # datasource
            tclass = list(ref_dict.keys())[0]
            cur_ds = tclass._datasource_name
            if cur_ds == self_ds_name:
                # Same datasource, the filter stay is self query
                result_rel_filters.append(((rfield, ref_dict), op, value))
            else:
                # Different datasource, we will have to create a subquery
                if cur_ds not in other_ds_filters:
                    other_ds_filters[cur_ds] = list()
                other_ds_filters[cur_ds].append(
                    ((rfield, ref_dict), op, value))
        #deduplication of std filters
        filters_cp = set()
        if not isinstance(filters_orig, set):
            for i, cfilt in enumerate(filters_orig):
                a, b, c = cfilt
                if isinstance(c, list): #list are not hashable
                    newc = tuple(c)
                else:
                    newc = c
                old_len = len(filters_cp)
                filters_cp |= set((a,b,newc))
                if len(filters_cp) == old_len:
                    del(filters_orig[i])
        # Sets _query_filter attribute of self query
        self._query_filter = (filters_orig, result_rel_filters)
        #Sub queries creation
        subq = list()
        for ds, rfilters in other_ds_filters.items():
            for rfilter in rfilters:
                (rfield, ref_dict), op, value = rfilter
                for tclass, tfield in ref_dict.items():
                    query = LeGetQuery(
                        target_class=tclass,
                        query_filters=[(tfield, op, value)],
                        field_list=[tfield])
                    subq.append((rfield, query))
        self.subqueries = subq

    ##@return informations
    def dump_infos(self):
        ret = super().dump_infos()
        ret['query_filter'] = self._query_filter
        ret['subqueries'] = self.subqueries
        return ret

    def __repr__(self):
        res = "<{classname} target={target_class} query_filter={query_filter}"
        res = res.format(
            classname=self.__class__.__name__,
            query_filter=self._query_filter,
            target_class=self._target_class)
        if len(self.subqueries) > 0:
            for n, subq in enumerate(self.subqueries):
                res += "\n\tSubquerie %d : %s"
                res %= (n, subq)
        res += '>'
        return res

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
    #- OP is one of the authorized comparison operands (see
    #@ref LeFilteredQuery.query_operators )
    #- VALUE is... a value
    #
    #@par Relational filters
    #
    #Those filters concerns on reference fields (see the corresponding
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
    #@warning Does not supports multiple UID for an EmClass
    def _prepare_filters(self, filters_l):
        filters=list()
        res_filters = list()
        rel_filters = list()
        err_l = dict()
        #Splitting in tuple if necessary
        for i, fil in enumerate(filters_l):
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
                err_l[field] = NameError("'%s' is not a valid relational \
field name" % field)
                continue
            # Checking field against target_class
            ret = self._check_field(self._target_class, field)
            if isinstance(ret, Exception):
                err_l[field] = ret
                continue
            field_datahandler = self._target_class.field(field)
            if isinstance(field_datahandler, Exception):
                err_l[field] = field_datahandler
                continue
            if ref_field is not None and not field_datahandler.is_reference():
                # inconsistency
                err_l[field] = NameError("The field '%s' in %s is not \
a relational field, but %s.%s was present in the filter"
                                            % (field,
                                                self._target_class.__name__,
                                                field,
                                                ref_field))
            if field_datahandler.is_reference():
                #Relationnal field
                if ref_field is None:
                    # ref_field default value
                    #
                    #   !!! WARNING !!!
                    # This piece of code does not supports multiple UID for an
                    # emclass
                    #
                    ref_uid = [
                        lc._uid[0] for lc in field_datahandler.linked_classes]

                    if len(set(ref_uid)) == 1:
                        ref_field = ref_uid[0]
                    else:
                        if len(ref_uid) > 1:
                            msg = "The referenced classes are identified by \
fields with different name. Unable to determine wich field to use for the \
reference"
                        else:
                            msg = "Unknow error when trying to determine wich \
field to use for the relational filter"
                        err_l[err_key] = RuntimeError(msg)
                        continue
                # Prepare relational field
                ret = self._prepare_relational_fields(field, ref_field)
                if isinstance(ret, Exception):
                    err_l[err_key] = ret
                    continue
                else:
                    value, error = field_datahandler.check_data_value(value)
                    rel_filters.append((ret, operator, value))
            else:
                value_orig = value
                value, error = field_datahandler.check_data_value(value)
                if isinstance(error, Exception):
                    value = value_orig
                res_filters.append((field,operator, value))
        if len(err_l) > 0:
            raise LeApiDataCheckErrors(
                                        "Error while preparing filters : ",
                                        err_l)
        return (res_filters, rel_filters)

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
            msg = "The query_filter '%s' seems to be invalid"
            raise ValueError(msg % query_filter)
        result = (
            matches.group('field'),
            re.sub(r'\s', ' ', matches.group('operator'), count=0),
            matches.group('value').strip())
        result = [r.strip() for r in result]
        for r in result:
            if len(r) == 0:
                msg = "The query_filter '%s' seems to be invalid"
                raise ValueError(msg % query_filter)
        return result

    ## @brief Compile the regex for query_filter processing
    # @note Set _LeObject._query_re
    @classmethod
    def __compile_query_re(cls):
        op_re_piece = '(?P<operator>(%s)'
        op_re_piece %= cls._query_operators[0].replace(' ', '\s')
        for operator in cls._query_operators[1:]:
            op_re_piece += '|(%s)'%operator.replace(' ', '\s')
        op_re_piece += ')'

        re_full = '^\s*(?P<field>([a-z_][a-z0-9\-_]*\.)?[a-z_][a-z0-9\-_]*)\s*'
        re_full += op_re_piece+'\s*(?P<value>.*)\s*$'

        cls._query_re = re.compile(re_full, flags=re.IGNORECASE)
        pass

    @classmethod
    def _check_field(cls, target_class, fieldname):
        try:
            target_class.field(fieldname)
        except NameError as e:
            msg = "No field named '%s' in %s'"
            msg %= (fieldname, target_class.__name__)
            return NameError(msg)

    ##@brief Prepare a relational filter
    #
    #Relational filters are composed of a tuple like the simple filters
    #but the first element of this tuple is a tuple to :
    #
    #<code>((FIELDNAME, {REF_CLASS: REF_FIELD}), OP, VALUE)</code>
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
    #          }
    #       ),
    #       ' IN ',
    #       [ 1,2,3,5 ])</pre>
    #@todo move the documentation to another place
    #
    #@param fieldname str : The relational field name
    #@param ref_field str|None : The referenced field name (if None use
    #uniq identifiers as referenced field
    #@return a well formed relational filter tuple or an Exception instance
    def _prepare_relational_fields(self, fieldname, ref_field=None):
        datahandler = self._target_class.field(fieldname)
        # now we are going to fetch the referenced class to see if the
        # reference field is valid
        ref_classes = datahandler.linked_classes
        ref_dict = dict()
        if ref_field is None:
            for ref_class in ref_classes:
                ref_dict[ref_class] = ref_class.uid_fieldname
        else:
            r_ds = None
            for ref_class in ref_classes:
                if r_ds is None:
                    r_ds = ref_class._datasource_name
                elif ref_class._datasource_name != r_ds:
                    return RuntimeError("All referenced class doesn't have the\
 same datasource. Query not possible")
                if ref_field in ref_class.fieldnames(True):
                    ref_dict[ref_class] = ref_field
                else:
                    msg = "Warning the class %s is not considered in \
the relational filter %s"
                    msg %= (ref_class.__name__, ref_field)
                    logger.debug(msg)
        if len(ref_dict) == 0:
            return NameError("No field named '%s' in referenced objects [%s]"
                                % (ref_field,
                                    ','.join([rc.__name__ for rc in ref_classes])))
        return (fieldname, ref_dict)


##@brief A query to insert a new object
class LeInsertQuery(LeQuery):
    _hook_prefix = 'leapi_insert_'
    _data_check_args = {'complete': True, 'allow_internal': False}

    def __init__(self, target_class):
        if target_class.is_abstract():
            raise LeApiQueryError("Trying to create an insert query on an \
abstract LeObject : %s" % target_class)
        super().__init__(target_class)
    
    ## @brief Implements an insert query operation, with only one insertion
    # @param new_datas : datas to be inserted
    def _query(self, datas):
        datas = self._target_class.prepare_datas(datas, True, False)
        id_inserted = self._rw_datasource.insert(self._target_class, datas)
        return id_inserted
    """
    ## @brief Implements an insert query operation, with multiple insertions
    # @param datas : list of **datas to be inserted
    def _query(self, datas):
        nb_inserted = self._datasource.insert_multi(
            self._target_class,datas_list)
        if nb_inserted < 0:
            raise LeApiQueryError("Multiple insertions error")
        return nb_inserted
    """

    ## @brief Execute the insert query
    def execute(self, datas):
        return super().execute(datas=datas)


##@brief A query to update datas for a given object
#
#@todo Change behavior, Huge optimization problem when updating using filters
#and not instance. We have to run a GET and then 1 update by fecthed object...
class LeUpdateQuery(LeFilteredQuery):
    _hook_prefix = 'leapi_update_'
    _data_check_args = {'complete': False, 'allow_internal': False}

    ##@brief Instanciate an update query
    #
    #If a class and not an instance is given, no query_filters are expected
    #and the update will be fast and simple. Else we have to run a get query
    #before updating (to fetch datas, update them and then, construct them
    #and check their consistency)
    #@param target LeObject clas or instance
    #@param query_filters list|None
    #@todo change strategy with instance update. We have to accept datas for
    #the execute method
    def __init__(self, target, query_filters=None):
        ##@brief This attr is set only if the target argument is an 
        #instance of a LeObject subclass
        self.__leobject_instance_datas = None
        target_class = target

        if not inspect.isclass(target):
            if query_filters is not None:
                msg = "No query_filters accepted when an instance is given as \
target to LeUpdateQuery constructor"
                raise AttributeError(msg)
            target_class = target.__class__
            if target_class.initialized:
                self.__leobject_instance_datas = target.datas(True)
            else:
                query_filters = [(target._uid[0], '=', target.uid())]

        super().__init__(target_class, query_filters)

    ##@brief Implements an update query
    #@param filters list : see @ref LeFilteredQuery
    #@param rel_filters list : see @ref LeFilteredQuery
    #@param datas dict : datas to update
    #@returns the number of updated items
    #@todo change stategy for instance update. Datas should be allowed
    #for execute method (and query)
    def _query(self, datas):
        uid_name = self._target_class._uid[0]
        if self.__leobject_instance_datas is not None:
            #Instance update
            #Building query_filter
            filters = [(
                uid_name, 
                '=', 
                str(self.__leobject_instance_datas[uid_name]))]
            res = self._rw_datasource.update(
                self._target_class, filters, [],
                self.__leobject_instance_datas)
        else:
            #Update by filters, we have to fetch datas before updating
            res = self._ro_datasource.select(
                self._target_class, self._target_class.fieldnames(True),
                self._query_filter[0],
                self._query_filter[1])
            #Checking and constructing datas
            upd_datas = dict()
            for res_data in res:
                res_data.update(datas)
                res_datas = self._target_class.prepare_datas(
                    res_data, True, True)
                filters = [(uid_name, '=', res_data[uid_name])]
                res = self._rw_datasource.update(
                    self._target_class, filters, [],
                    res_datas)
        return res

    ## @brief Execute the update query
    def execute(self, datas=None):
        if self.__leobject_instance_datas is not None and datas is not None:
            raise LeApiQueryError("No datas expected when running an update \
query on an instance")
        if self.__leobject_instance_datas is None and datas is None:
            raise LeApiQueryError("Datas are mandatory when running an update \
query on a class with filters")
        return super().execute(datas=datas)


##@brief A query to delete an object
class LeDeleteQuery(LeFilteredQuery):
    _hook_prefix = 'leapi_delete_'

    def __init__(self, target_class, query_filter):
        super().__init__(target_class, query_filter)

    ## @brief Execute the delete query
    def execute(self, datas=None):
        return super().execute()

    ##@brief Implements delete query operations
    #@param filters list : see @ref LeFilteredQuery
    #@param rel_filters list : see @ref LeFilteredQuery
    #@returns the number of deleted items
    def _query(self, datas=None):
        filters, rel_filters = self._query_filter
        nb_deleted = self._rw_datasource.delete(
            self._target_class, filters, rel_filters)
        return nb_deleted

class LeGetQuery(LeFilteredQuery):
    _hook_prefix = 'leapi_get_'

    ##@brief Instanciate a new get query
    #@param target_class LeObject : class of object the query is about
    #@param query_filters dict : {OP, list of query filters}
    # or tuple (FIELD, OPERATOR, VALUE) )
    #@param field_list list|None : list of string representing fields see
    # @ref leobject_filters
    #@param order list : A list of field names or tuple (FIELDNAME,[ASC | DESC])
    #@param group list : A list of field names or tuple (FIELDNAME,[ASC | DESC])
    #@param limit int : The maximum number of returned results
    #@param offset int : offset
    def __init__(self, target_class, query_filters, **kwargs):
        super().__init__(target_class, query_filters)
        ##@brief The fields to get
        self._field_list = None
        ##@brief An equivalent to the SQL ORDER BY
        self._order = None
        ##@brief An equivalent to the SQL GROUP BY
        self._group = None
        ##@brief An equivalent to the SQL LIMIT x
        self._limit = None
        ##@brief An equivalent to the SQL LIMIT x, OFFSET
        self._offset = 0

        # Checking kwargs and assigning default values if there is some
        for argname in kwargs:
            if argname not in (
                'field_list', 'order', 'group', 'limit', 'offset'):
                raise TypeError("Unexpected argument '%s'" % argname)

        if 'field_list' not in kwargs:
            self.set_field_list(target_class.fieldnames(include_ro = True))
        else:
            self.set_field_list(kwargs['field_list'])

        if 'order' in kwargs:
            #check kwargs['order']
            self._order = kwargs['order']
        if 'group' in kwargs:
            #check kwargs['group']
            self._group = kwargs['group']
        if 'limit' in kwargs and kwargs['limit'] is not None:
            try:
                self._limit = int(kwargs['limit'])
                if self._limit <= 0:
                    raise ValueError()
            except ValueError:
                msg = "limit argument expected to be an interger > 0"
                raise ValueError(msg)
        if 'offset' in kwargs:
            try:
                self._offset = int(kwargs['offset'])
                if self._offset < 0:
                    raise ValueError()
            except ValueError:
                msg = "offset argument expected to be an integer >= 0"
                raise ValueError(msg)

    ##@brief Set the field list
    # @param field_list list | None : If None use all fields
    # @return None
    # @throw LeApiQueryError if unknown field given
    def set_field_list(self, field_list):
        err_l = dict()
        if field_list is not None:
            for fieldname in field_list:
                ret = self._check_field(self._target_class, fieldname)
                if isinstance(ret, Exception):
                    msg = "No field named '%s' in %s"
                    msg %= (fieldname, self._target_class.__name__)
                    expt = NameError(msg)
                    err_l[fieldname] =  expt
            if len(err_l) > 0:
                msg = "Error while setting field_list in a get query"
                raise LeApiQueryErrors(msg = msg, exceptions = err_l)
            self._field_list = list(set(field_list))

    ##@brief Execute the get query
    def execute(self, datas=None):
        return super().execute()

    ##@brief Implements select query operations
    # @returns a list containing the item(s)
    def _query(self, datas=None):
        # select datas corresponding to query_filter
        fl = list(self._field_list) if self._field_list is not None else None
        l_datas=self._ro_datasource.select(
            target = self._target_class,
            field_list = fl,
            filters = self._query_filter[0], 
            relational_filters = self._query_filter[1], 
            order = self._order, 
            group = self._group, 
            limit = self._limit, 
            offset = self._offset)
        return l_datas

    ##@return a dict with query infos
    def dump_infos(self):
        ret = super().dump_infos()
        ret.update({  'field_list' : self._field_list, 
                        'order' : self._order, 
                        'group' : self._group, 
                        'limit' : self._limit, 
                        'offset': self._offset, 
       })
        return ret

    def __repr__(self):
        res = "<LeGetQuery target={target_class} filter={query_filter} \
field_list={field_list} order={order} group={group} limit={limit} \
offset={offset}"
        res = res.format(**self.dump_infos())
        if len(self.subqueries) > 0:
            for n,subq in enumerate(self.subqueries):
                res += "\n\tSubquerie %d : %s"
                res %= (n, subq)
        res += ">"
        return res


