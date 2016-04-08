#-*- coding: utf-8 -*-

import re
from .leobject import LeObject, LeApiErrors, LeApiDataCheckError


class LeQueryError(Exception):
    pass


class LeQuery(object):

    ## @brief The datasource object used for this query
    _datasource = None

    ## @brief The available operators used in query definitions
    _query_operators = ['=', '<=', '>=', '!=', '<', '>', ' in ', ' not in ', ' like ', ' not like ']

    def __init__(self, target_class):
        if not issubclass(target_class, LeObject):
            raise TypeError("target class has to be a child class of LeObject")
        self._target_class = target_class


class LeInsertQuery(LeQuery):
    action = 'insert'

    def __init__(self, target_class, datas, classname=None):
        targeted_class = target_class if classname is None else LeObject.name2class(classname)
        if not targeted_class:
            raise LeQueryError('Error when inserting', {'error': ValueError("The class '%s' was not found" % classname)})

        super().__init__(targeted_class)
        self.datas = datas

    # @todo Reactivate the LodelHooks call when this class is implemented
    def execute(self):
        datas = self.datas  # TODO : replace with LodelHooks.call_hook('leapi_insert_pre', self._target_class, self.datas)
        ret = self.__insert(**datas)
        # ret = LodelHook.call_hook('leapi_insert_post', self._target_class, ret)
        return ret

    def __insert(self):
        insert_datas = self._target_class.prepare_datas(self.datas, complete=True, allow_internal=True)
        return self._datasource.insert(self._target_class, **insert_datas)


class LeFilteredQuery(LeQuery):

    def __init__(self, target_class):
        super().__init__(target_class)

    @classmethod
    def validate_query_filters(cls, query_filters):
        for query_filter in query_filters:
            if query_filter[1] not in cls._query_operators:
                raise LeQueryError("The operator %s is not valid." % query_filter[1])
        return True

    @classmethod
    def is_relational_field(cls, field):
        return field.startswith('superior.') or field.startswith('subordinate.')

class LeGetQuery(LeFilteredQuery):

    def __init__(self, target_class, target_uid, query_filters, field_list=None, order=None, group=None, limit=None, offset=0, instanciate=True):
        super().__init__(target_class)
        self.query_filters = query_filters
        self.default_field_list = []
        self.field_list = field_list if field_list is not None else self._target_class.fieldnames()
        self.order = order
        self.group = group
        self.limit = limit
        self.offset = offset
        self.instanciate = instanciate
        self.target_object = None  # TODO get an instance of the target_class using a unique id

    def execute(self):
        datas = self.datas  # TODO : replace with LodelHook.call_hook('leapi_get_pre', self.target_object, self.datas)
        ret = self.__get(**datas)
        # ret = LodelHook.call_hook('leapi_get_post', self.target_object, ret)
        return ret

    def __get(self, **kwargs):
        field_list = self.__prepare_field_list(self.field_list)  #TODO implement the prepare_field_list method

        query_filters, relational_filters = self.__prepare_filters()

        # Preparing order
        if self.order:
            order = self.__prepare_order()
            if isinstance(order, Exception):
                raise order  # can be buffered and raised later, but _prepare_filters raise when fails

        # Preparing group
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

    def __prepare_field_list(self):
        errors = dict()
        ret_field_list = list()
        for field in self.field_list:
            if self.is_relational(field):
                ret = self.__prepare_relational_fields(field)
            else:
                ret = self.__check_field(field)

            if isinstance(ret, Exception):
                errors[field] = ret
            else:
                ret_field_list.append(ret)

        if len(errors) > 0:
            raise LeApiDataCheckError(errors)

        return ret_field_list

    def __prepare_relational_fields(self, field):
        # TODO Implement the method
        return field

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

    def __check_field(self, target_object, field):
        if field not in self.target_object.fieldnames():
            return ValueError("No such field '%s' in %s" % (field, self.target_object.__class__))
        return field

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
            ret = self.__check_field(self.target_object, field)
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
        datas['target_object'] = self.target_object
        return datas

    def __prepare_order(self):
        errors = dict()
        result = []
        for order_field in self.order:
            if not isinstance(order_field, tuple):
                order_field = (order_field, 'ASC')
            if len(order_field) != 2 or order_field[1].upper() not in ['ASC', 'DESC']:
                errors[order_field] = ValueError("Expected a string or a tuple with (FIELDNAME, ['ASC'|'DESC']) but got : %s" % order_field)
            else:
                ret = self._target_class.check_field(order_field[0])
                if isinstance(ret, Exception):
                    errors[order_field] = ret
            order_field = (order_field[0], order_field[1].upper())
            result.append(order_field)

        if len(errors) > 0:
            return LeApiErrors("Errors when preparing ordering fields", errors)
        return result


class LeUpdateQuery(LeFilteredQuery):

    def __init__(self, target_class, target_uid, query_filters):
        super().__init__(target_class)
        self.query_filters = query_filters
        self.target_uid = target_uid
        self.target_object = None  # TODO get an instance of the target_class using a unique id

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
        ret = self._datasource.update(self.target_uid, **updated_datas)  # TODO add the correct arguments for the datasource's method call
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