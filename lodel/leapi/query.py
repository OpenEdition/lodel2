#-*- coding: utf-8 -*-

from leobject import LeObject


class LeQueryError(Exception):
    pass


## @brief Handle CRUD operations on datasource
class LeQuery(object):

    ## @brief The datasource object used for this Query class
    _datasource = None

    ## @brief the operators map
    # assigns the right operator for a string based key (ex: "lte" => "<=" )
    _query_operators_map = {}

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
    def execute_query(self):
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


## @brief Handles Delete queries
class LeDeleteQuery(LeFilteredQuery):
    # Name of the corresponding action
    action = 'delete'

if __name__ == "__main__":
    class MyObject(LeObject):
        def __init__(self):
            super().__init__()
        @staticmethod
        def is_abstract():
            return False
        def __str__(self):
	    return 'MyObject'

    my_insert_query = LeInsertQuery(MyObject)
    print(my_insert_query.prepare_query({'test':'ok'}))
