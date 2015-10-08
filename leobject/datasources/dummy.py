#-*- coding: utf-8 -*-


## dummy datasource for LeObject
# This class has to be extended to apply to a real datasource
# But it can be used as an empty and debug datasource

class DummyDatasource(object):

    def __init__(self, options=None):
        self.options = options

    ## @brief create a new LeObject
    # @param data dict: a dictionnary of field:value to save
    # @return lodel_id int: new lodel_id of the newly created LeObject
    def insert(self, data):
        print("DummyDatasource.insert: ", data)
        return 42

    ## @brief update an existing LeObject
    # @param lodel_id int | (int): lodel_id of the object(s) where to apply changes
    # @param data dict: dictionnary of field:value to save
    # @param update_filters string | (string): list of string of update filters
    # @return okay bool: True on success, it will raise on failure
    def update(self, lodel_id, data, update_filters=None):
        print("DummyDatasource.update: ", lodel_id, data, update_filters)

        return True

    ## @brief delete an existing LeObject
    # @param lodel_id int | (int): lodel_id of the object(s) to delete
    # @param delete_filters string | (string): list of string of delete filters
    # @return okay bool: True on success, it will raise on failure
    def delete(self, lodel_id, delete_filters=None):
        print("DummyDatasource.delete: ", lodel_id, delete_filters)

        return True

    ## @brief make a search to retrieve a collection of LeObject
    # @param query_filters string | (string): list of string of query filters
    # @return responses ({string:*}): a list of dict with field:value
    def get(self, query_filters):
        print("DummyDatasource.get: ", query_filters)

        return False
