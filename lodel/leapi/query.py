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

    def __init__(self, target_class):
        super().__init__(target_class)
        if target_class.is_abstract():
            raise LeQueryError("Target EmClass cannot be abstract for an InsertQuery")

    def prepare_query(self, datas=None):
        if datas is None or len(datas.keys()) == 0:
            raise LeQueryError("No query datas found")

        query = {}
        query['action'] = self.__class__.action
        query['target'] = self._target_class
        for key, value in datas.items():
            query[key] = value

        return query


## @brief Handles Le*Query with a query_filter argument
# @see LeGetQuery, LeUpdateQuery, LeDeleteQuery
class LeFilteredQuery(LeQuery):
    pass


## @brief Handles Get queries
class LeGetQuery(LeFilteredQuery):
    # Name of the corresponding action
    action = 'get'


## @brief Handles Update queries
class LeUpdateQuery(LeFilteredQuery):
    # Name of the corresponding action
    action = 'update'

    def __init__(self, datas=None):
        self.datas = datas if datas is None else locals()
        del(self.datas['self'])

    ## @brief executes the query, with corresponding hooks
    # @return dict
    def execute(self):
        # LodelHook.call_hook('leapi_update_pre', self, None)
        ret = self.update()
        return self.after_update(ret)

    ## @brief calls before-update hook(s)
    # @return dict
    # @todo to be implemented
    def before_update(self):
        return self.datas

    ## @brief calls hook(s) after the update process
    # @param ret : returned results
    # @return bool : True if success
    # @todo to be implemented
    def after_update(self, ret):
        return ret

    ## @brief performs the update in the datasource
    # @TODO the call to _datasource.update() will be changed when the corresponding method is implemented
    # @TODO in case of an error, we should add code to manage it
    def update(self):
        if 'uid' not in self.datas:
            raise LeQueryError("No object uid given to the query. The update can't be performed")
        updated_datas = self.prepare_query()
        ret = self._datasource.update(self.datas['uid'], **updated_datas)
        if ret == 1:
            return True
        return False

    ## @brief checks and prepare datas
    # @return dict
    def prepare_query(self):
        ret_datas = self.check_datas_value(self.datas)
        if isinstance(ret_datas, Exception):
            raise ret_datas
        ret_datas = self.construct_datas(ret_datas)
        self.check_datas_consistency(ret_datas)
        return ret_datas

    def check_datas_value(self, datas):
        err_l = dict()  # Stores all errors occurring during the process
        correct = []  # Valid fields name
        mandatory = []  # mandatory fields name
        pass

    def construct_datas(self, datas):
        pass

    def check_datas_consistency(self, datas):
        pass


## @brief Handles Delete queries
class LeDeleteQuery(LeFilteredQuery):
    # Name of the corresponding action
    action = 'delete'
