#-*- coding: utf-8 -*-

## Main class to handle objects defined by the types of an Editorial Model
# an instance of these objects is pedantically called LeObject !

from EditorialModel.types import EmType

class _LeObject(object):
    
    ## @brief The editorial model
    _model = None
    ## @brief The datasource
    _datasource = None
    
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
    # @param query_filters string | (string): list of string of query filters
    # @return responses ({string:*}): a list of dict with field:value
    def get(self, query_filters):
        try:
            datasource_filters = self._prepare_filters(query_filters)
            responses = self.datasource.get(datasource_filters)
        except:
            raise

        return responses

    ## @brief check if data dict fits with the model
    # @param data dict: dictionnary of field:value to check
    # @return checked_data ({string:*}): a list of dict with field:value
    # @todo implent !
    def _check_data(self, data):
        checked_data = data
        return checked_data

    ## @brief check and prepare query for the datasource
    # @param query_filters (string): list of string of query filters
    # @todo implent !
    def _prepare_filters(self, query_filters):
        if query_filters is None:
            return ()
        elif isinstance(query_filters[0], str):
            query_filters = (query_filters)
        
        fields, operators, queries = zip(*query_filters)
        
        # find name of the type in filters
        try:
            type_index = fields.index('type')
            if operators[type_index] != '=':
                raise ValueError
            type_name = queries[type_index]
            del query_filters[type_index]
        except ValueError:
            print ("Le champ type est obligatoire dans une requête")
            raise

        
        comps = self.model.components(EmType)
        for comp in comps:
            if comp.name == type_name:
                em_type = comp
                break
        
        class_name = em_type.em_class.name
        fields = em_type.fields()
        field_list = [f.name for f in fields]
        print (em_type, class_name, type_name, fields, field_list)

        prepared_filters = query_filters
        return prepared_filters
