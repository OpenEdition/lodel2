#-*- coding: utf-8 -*-

## Generic DataSource for LeObject

class LeDataSource(object):

    def __init__(self, options=None):
        self.options = options


    ## @brief Update
    # @param lodel_id int|(int) : id(s) of the object(s) where to apply changes
    # @param data dict : dictionnary of field:value to save
    # @param update_filters string | (string) : list of string of updata filters
    def update(self, lodel_id, data, update_filters=None):
        pass

    