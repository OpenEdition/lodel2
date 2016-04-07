#-*- coding: utf-8 -*-

from .leobject import LeObject


class LeQueryError(Exception):
    pass


## @brief Handle CRUD operations on datasource
class LeQuery(object):

    ## @brief The datasource object used for this Query class
    _datasource = None

    ## @brief the operators used in query definitions
    _query_operators_map = ['=', '<=', '>=', '!=', '<', '>', ' in ', ' not in ', ' like ', ' not like ']

    ## @brief Constructor
    # @param target_class LeObject class or childs : The LeObject child class concerned by this query
    def __init__(self, target_class):
        if not issubclass(target_class, LeObject):
            raise TypeError("target_class have to be a child class of LeObject")
        self._target_class = target_class

    ## @brief Prepares the query by formatting it into a dictionary
    # @param datas dict: query parameters
    # @return dict : The formatted query
    def prepare_query(self, datas=None):
        return {}

    ## @brief Executes the query
    # @return dict : The results of the query
    def execute(self):
        return {}


## @brief Handles insert queries
class LeInsertQuery(LeQuery):

    # Name of the corresponding action
    action = 'insert'

    def __init__(self, datas=None):
        self.datas = datas if datas is not None else locals()
        del(self.datas['self'])

    def execute(self):
        pass

    def insert(self):
        pass

    def prepare_query(self, datas=None):
        pass

## @brief Handles Le*Query with a query_filter argument
# @see LeGetQuery, LeUpdateQuery, LeDeleteQuery
class LeFilteredQuery(LeQuery):
    pass


## @brief Handles Get queries
class LeGetQuery(LeFilteredQuery):
    # Name of the corresponding action
    action = 'get'

    def __init__(self, datas=None):
        self.datas = datas if datas is not None else locals()
        del(self.datas['self'])
        self.field_list = []  # TODO Add the default field list definition method

    def execute(self):
        datas = self.datas  # TODO : replace with LodelHook.call_hook('leapi_get_pre', self, self.datas)
        ret = self.get(**datas)
        # ret = LodelHook.call_hook('leapi_get_post', self, ret)
        return ret

    ## @brief performs the select action in the datasource
    # @TODO add the management of filters, groups, order, and change the call to _datasource.select
    def get(self, **kwargs):
        field_list = kwargs['field_list'] if 'field_list' in kwargs else self.field_list
        field_list = self.prepare_field_list(field_list)  # TODO Implement the prepare_field_list method

        # checks the limit and offset values
        if 'limit' in self.datas:
            if self.datas['limit'] is not None and self.datas['limit'] <= 0:
                raise ValueError('Invalid limit given : %d' % self.datas['limit'])

        if 'offset' in self.datas:
            if self.datas['offset'] is not None and self.datas['offset'] < 0:
                raise ValueError("Invalid offset given : %d" % self.datas['offset'])

        results = self._datasource.select()
        return results

    def prepare_field_list(self):
        pass

    def prepare_filters(self):
        pass

    def prepare_order(self):
        pass

    def prepare_groups(self):
        pass

## @brief Handles Update queries
class LeUpdateQuery(LeFilteredQuery):
    # Name of the corresponding action
    action = 'update'

    def __init__(self, datas=None):
        self.datas = datas if datas is not None else locals()
        del(self.datas['self'])

    ## @brief executes the query, call the corresponding hooks
    # @return dict
    # @TODO reactivate the calls to the hooks when they are implemented
    def execute(self):
        # LodelHook.call_hook('leapi_update_pre', self, None)
        ret = self.update()
        # ret = LodelHook.call_hook('leapi_update_post', self, ret)
        return ret

    ## @brief performs the update in the datasource
    # @TODO change the call to _datasource.update() according to its implementation in the DataSource class
    # @TODO Add a better behavior in case of error
    def update(self):
        if 'uid' not in self.datas:
            raise LeQueryError("No object uid given to the query. The update can't be performed")
        updated_datas = self.prepare_query()
        ret = self._datasource.update(self.datas['uid'], **updated_datas)
        if ret == 1:
            return True
        else:
            return False

    ## @brief prepares the datas for the query
    # @return dict
    def prepare_query(self):
        ret_datas = self.check_datas_value()
        if isinstance(ret_datas, Exception):
            raise LeQueryError("One or more query datas' value(s) is(are) not valid")
        ret_datas = self.construct_datas(ret_datas)
        self.check_datas_consistency(ret_datas)
        return ret_datas


    def check_datas_value(self, datas):
        pass

    def construct_datas(self, datas):
        pass

    def check_datas_consistency(self, datas):
        pass


## @brief Handles Delete queries
class LeDeleteQuery(LeFilteredQuery):
    # Name of the corresponding action
    action = 'delete'

    def __init__(self, datas=None):
        self.datas = datas
        if 'uid' not in self.datas:
            raise LeQueryError('No uid specified for deletion.')

    def delete(self):
        # LodelHook.call_hook('leapi_delete_pre', self, None)
        ret = self._datasource.delete(self.datas)
        # ret = LodelHook.call_hook('leapi_delete_post', self, ret)
        return ret
