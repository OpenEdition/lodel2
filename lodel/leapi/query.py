#-*- coding: utf-8 -*-

import re
from .leobject import LeObject, LeApiErrors, LeApiDataCheckError


class LeQueryError(Exception):
    pass

class LeQuery(object):

    ## @brief The datasource object used for this query
    datasource = None

    ## @brief The available operators used in query definitions
    query_operators = ['=', '<=', '>=', '!=', '<', '>', ' in ', ' not in ', ' like ', ' not like ']

    ## @brief Constructor
    # @param target_class EmClass : class of the object to query about
    def __init__(self, target_class):
        if not issubclass(target_class, LeObject):
            raise TypeError("target class has to be a child class of LeObject")
        self.target_class = target_class


## @brief Class representing an Insert query
class LeInsertQuery(LeQuery):

    ## @brief Constructor
    # @param target_class EmClass: class corresponding to the inserted object
    # @param datas dict : datas to insert
    def __init__(self, target_class, datas):
        super().__init__(target_class)
        self.datas = datas

    ## @brief executes the insert query
    # @return bool
    # @TODO reactivate the LodelHooks call when this class is implemented
    def execute(self):
        datas = self.datas  # LodelHooks.call_hook('leapi_insert_pre', self.target_class, self.datas)
        ret = self.__insert(**datas)
        # ret = LodelHook.call_hook('leapi_insert_post', self.target_class, ret)
        return ret

    ## @brief calls the datasource to perform the insert command
    # @param datas dict : formatted datas corresponding to the insert
    # @return str : the uid of the inserted object
    def __insert(self, **datas):
        insert_datas = self.target_class.prepare_datas(datas, complete=True, allow_internal=True)
        res = self.datasource.insert(self.target_class, **insert_datas)
        return res


## @brief Class representing an Abstract Filtered Query
class LeFilteredQuery(LeQuery):

    ## @brief Constructor
    # @param target_class EmClass : Object of the query
    def __init__(self, target_class):
        super().__init__(target_class)

    ## @brief Validates the query filters
    # @param query_filters list
    # @return bool
    # @raise LeQueryError if one of the filter is not valid
    @classmethod
    def validate_query_filters(cls, query_filters):
        for query_filter in query_filters:
            if query_filter[1] not in cls.query_operators:
                raise LeQueryError("The operator %s is not valid." % query_filter[1])
        return True

    ## @brief Checks if a field is relational
    # @param field str : Name of the field
    # @return bool
    @classmethod
    def is_relational_field(cls, field):
        return field.startswith('superior.') or field.startswith('subordinate.')


## @brief Class representing a Get Query
class LeGetQuery(LeFilteredQuery):

    ## @brief Constructor
    # @param target_class EmClass : main class
    # @param query_filters
    # @param field_list list
    # @param order list : list of tuples corresponding to the fields used to sort the results
    # @param group list : list of tuples corresponding to the fields used to group the results
    # @param limit int : Maximum number of results to get
    # @param offset int
    # @param instanciate bool : if True, objects will be returned instead of dictionaries
    def __init__(self, target_class, query_filters, field_list=None, order=None, group=None, limit=None, offset=0, instanciate=True):
        super().__init__(target_class)
        self.query_filters = query_filters
        self.default_field_list = []
        self.field_list = field_list if field_list is not None else self.target_class.fieldnames()
        self.order = order
        self.group = group
        self.limit = limit
        self.offset = offset
        self.instanciate = instanciate

    ## @brief executes the query
    # @return list
    # @TODO activate LodelHook calls
    def execute(self):
        datas = self.datas  # LodelHook.call_hook('leapi_get_pre', self.target_object, self.datas)
        ret = self.__get(**datas)
        # ret = LodelHook.call_hook('leapi_get_post', self.target_object, ret)
        return ret

    def __get(self, **datas):
        field_list = self.__prepare_field_list(self.field_list)

        query_filters, relational_filters = self.__prepare_filters()

        # Preparing the "order" parameters
        if self.order:
            order = self.__prepare_order()
            if isinstance(order, Exception):
                raise order  # can be buffered and raised later, but __prepare_filters raise when fails

        # Preparing the "group" parameters
        if self.group:
            group = self.__prepare_order()
            if isinstance(group, Exception):
                raise group  # can be buffered and raised later

        # checks the limit and offset values
        if self.limit is not None and self.limit <= 0:
            raise ValueError('Invalid limit given')

        if self.offset is not None and self.offset < 0:
            raise ValueError('Invalid offset given : %d' % self.offset)

        results = self._datasource.select()  # TODO add the correct arguments for the datasource's method call
        return results

    ## @brief prepares the field list
    # @return list
    # @raise LeApiDataCheckError
    def __prepare_field_list(self):
        errors = dict()
        ret_field_list = list()
        for field in self.field_list:
            if self.is_relational(field):
                ret = self.__prepare_relational_field(field)
            else:
                ret = self.__check_field(field)

            if isinstance(ret, Exception):
                errors[field] = ret
            else:
                ret_field_list.append(ret)

        if len(errors) > 0:
            raise LeApiDataCheckError(errors)

        return ret_field_list

    ## @brief prepares a relational field
    def __prepare_relational_field(self, field):
        # TODO Implement the method
        return field

    ## @brief splits the filter string into a tuple (FIELD, OPERATOR, VALUE)
    # @param filter str
    # @return tuple
    # @raise ValueError
    def __split_filter(self, filter):
        if self.query_re is None:
            self.__compile_query_re()

        matches = self.query_re.match(filter)
        if not matches:
            raise ValueError("The query_filter '%s' seems to be invalid" % filter)

        result = (matches.group('field'), re.sub(r'\s', ' ', matches.group('operator')), matches.group('value').strip())
        for r in result:
            if len(r) == 0:
                raise ValueError("The query_filter '%s' seems to be invalid" % filter)

        return result

    def __compile_query_re(self):
        op_re_piece = '(?P<operator>(%s)' % self._query_operators[0].replace(' ', '\s')
        for operator in self._query_operators[1:]:
            op_re_piece += '|(%s)' % operator.replace(' ', '\s')
        op_re_piece += ')'
        self.query_re = re.compile('^\s*(?P<field>(((superior)|(subordinate))\.)?[a-z_][a-z0-9\-_]*)\s*'+op_re_piece+'\s*(?P<value>[^<>=!].*)\s*$', flags=re.IGNORECASE)

    ## @brief checks if a field is in the target class of the query
    # @param field str
    # @return str
    # @raise ValueError
    def __check_field(self, field):
        if field not in self.target_class.fieldnames():
            return ValueError("No such field '%s' in %s" % (field, self.target_class))
        return field

    ## @brief Prepares the filters (relational and others)
    # @return tuple
    def __prepare_filters(self):
        filters = list()
        errors = dict()
        res_filters = list()
        rel_filters = list()

        # Splitting in tuple if necessary
        for filter in self.query_filters:
            if len(filter) == 3 and not isinstance(filter, str):
                filters.append(tuple(filter))
            else:
                filters.append(self.__split_filter(filter))

        for field, operator, value in filters:
            # TODO check the relation filters
            ret = self.__check_field(field)
            if isinstance(ret, Exception):
                errors[field] = ret
            else:
                res_filters.append((ret, operator, value))

        if len(errors) > 0:
            raise LeApiDataCheckError("Error while preparing filters : ", errors)

        return (res_filters, rel_filters)


        datas = dict()
        if LeFilteredQuery.validate_query_filters(self.query_filters):
            datas['query_filters'] = self.query_filters
        datas['target_class'] = self.target_class
        return datas

    ## @brief prepares the "order" parameters
    # @return list
    def __prepare_order(self):
        errors = dict()
        result = []
        for order_field in self.order:
            if not isinstance(order_field, tuple):
                order_field = (order_field, 'ASC')
            if len(order_field) != 2 or order_field[1].upper() not in ['ASC', 'DESC']:
                errors[order_field] = ValueError("Expected a string or a tuple with (FIELDNAME, ['ASC'|'DESC']) but got : %s" % order_field)
            else:
                ret = self.target_class.check_field(order_field[0])
                if isinstance(ret, Exception):
                    errors[order_field] = ret
            order_field = (order_field[0], order_field[1].upper())
            result.append(order_field)

        if len(errors) > 0:
            raise LeApiErrors("Errors when preparing ordering fields", errors)
        return result


class LeUpdateQuery(LeFilteredQuery):

    def __init__(self, target_class, target_uid, query_filters):
        super().__init__(target_class)
        self.query_filters = query_filters
        self.target_uid = target_uid

    def execute(self):
        # LodelHook.call_hook('leapi_update_pre', self.target_object, None)
        ret = self.__update()
        # ret = LodelHook.call_hook('leapi_update_post', self.target_object, ret)
        return ret

    ## @brief calls the datasource's update method and the corresponding hooks
    # @return bool
    # @TODO change the behavior in case of error in the update process
    def __update(self):
        updated_datas = self.__prepare()
        ret = self.datasource.update(self.target_uid, **updated_datas)  # TODO add the correct arguments for the datasource's method
        if ret == 1:
            return True
        else:
            return False

    ## @brief prepares the query_filters to be used as argument for the datasource's update method
    def __prepare(self):
        datas = dict()
        if LeFilteredQuery.validate_query_filters(self.query_filters):
            datas['query_filters'] = self.query_filters

        datas['target_uid'] = self.target_uid
        datas['target_class'] = self._target_class
        return datas


class LeDeleteQuery(LeFilteredQuery):

    def __init__(self, target_class, target_uid, query_filters):
        super().__init__(self._target_class)
        self.target_uid = target_uid
        self.query_filters = query_filters

    def execute(self):
        # LodelHook.call_hook('leapi_delete_pre', self.target_uid, None)
        ret = self.__delete()
        # ret = LodelHook.call('leapi_delete_post', self.target_object, ret)
        return ret

    ## @brief calls the datasource's delete method
    # @return bool
    # @TODO change the behavior in case of error in the update process
    def __delete(self):
        delete_datas = self.__prepare()
        ret = self._datasource.delete(**delete_datas)
        return ret

    def __prepare(self):
        datas = dict()
        if LeFilteredQuery.validate_query_filters(self.query_filters):
            datas['query_filters'] = self.query_filters

        datas['target_uid'] = self.target_uid
        datas['target_class'] = self._target_class

        return datas
