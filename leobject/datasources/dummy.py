#-*- coding: utf-8 -*-

## @brief Dummy datasource for LeObject
#
# This class has to be extended to apply to a real datasource
# But it can be used as an empty and debug datasource
class DummyDatasource(object):

    def __init__(self, module=None, *conn_args, **conn_kargs):
        self.module = module
        self.conn_args = conn_args
        self.conn_kargs = conn_kargs

    ## @brief update an existing LeObject
    # @param letype LeType : LeType child class
    # @param leclass LeClass : LeClass child class
    # @param filters list : List of filters (see @ref leobject_filters )
    # @param rel_filters list : List of relationnal filters (see @ref leobject_filters )
    # @param data dict : Dict representing fields and there values
    # @return True if success
    def update(self, letype, leclass, filters, rel_filters, data):
        print ("DummyDatasource.update: ", letype, leclass, filters, rel_filters, data)
        return True

    ## @brief create a new LeObject
    # @param letype LeType : LeType child class
    # @param leclass LeClass : LeClass child class
    # @param data list: a lis of dictionnary of field:value to save
    # @return lodel_id int: new lodel_id of the newly created LeObject
    def insert(self, letype, leclass, datas):
        print("DummyDatasource.insert: ", letype, leclass, datas)
        return 42

    ## @brief delete an existing LeObject
    # @param letype LeType : LeType child class
    # @param leclass LeClass : LeClass child class
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE) (see @ref leobject_filters )
    # @param relational_filters list : relationnal filters list (see @ref leobject_filters )
    # @return okay bool: True on success, it will raise on failure
    def delete(self, letype, leclass, filters, relational_filters):
        print("DummyDatasource.delete: ", letype, leclass, filters, relational_filters)
        return True

    ## @brief search for a collection of objects
    # @param leclass LeClass : LeClass instance
    # @param letype LeType : LeType instance
    # @param field_list list : list of fields to get from the datasource
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE) (see @ref leobject_filters )
    # @param relational_filters list : relationnal filters list (see @ref leobject_filters )
    # @return responses ({string:*}): a list of dict with field:value
    def get(self, leclass, letype, field_list, filters, relational_filters):
        print("DummyDatasource.get: ", leclass, letype, field_list, filters, relational_filters)
        return []
    
    ## @brief Add a superior to a LeObject
    # @note in the MySQL version the method will have a depth=None argument to allow reccursive calls to add all the path to the root with corresponding depth
    # @param lesup LeType | LeRoot : superior LeType child class instance or @ref
    # @param lesub LeType : subordinate LeType child class instance
    # @param nature str : A relation nature @ref EditorialModel.classtypesa
    # @param rank int : The rank of this relation
    # @param depth None|int : The depth of the relation (used to make reccursive calls in order to link with all superiors)
    # @return The relation ID or False if fails
    def add_superior(self, lesup, lesub, nature, rank, depth = None):
        pass

    ## @brief Delete a superior to a LeObject
    # @param lesup LeType : superior LeType child class instance
    # @param lesub Letype : subordinate LeType child class instance
    # @param nature str : A relation nature @ref EditorialModel.classtypes
    # @return True if deleted
    def del_superior(self, lesup, lesub, nature):
        pass

    ## @brief Fetch a superiors list ordered by depth for a LeType
    # @param lesub LeType : subordinate LeType child class instance
    # @param nature str : A relation nature @ref EditorialModel.classtypes
    # @return A list of LeType ordered by depth (the first is the direct superior)
    def get_superiors(self, lesub, nature):
        pass

    ## @brief Fetch the list of the subordinates given a nature
    # @param lesup LeType : superior LeType child class instance
    # @param nature str : A relation nature @ref EditorialModel.classtypes
    # @return A list of LeType ordered by rank that are subordinates of lesup in a "nature" relation
    def get_subordinates(self, lesup, nature):
        pass


    ## @brief Make a relation between 2 LeType
    # @note rel2type relations. Superior is the LeType from the EmClass and subordinate the LeType for the EmType
    # @param lesup LeType : LeType child class instance that is from the EmClass containing the rel2type field
    # @param lesub LeType : LeType child class instance that is from the EmType linked by the rel2type field ( @ref EditorialModel.fieldtypes.rel2type.EmFieldType.rel_to_type_id )
    # @param rank int : Begin at 0 ?
    # @return The relation_id if success else return False
    def add_related(self, lesup, lesub, rank = 'last', **rel_attr):
        pass
    
    ## @brief Returns related LeType
    # @param leo LeType : The from LeType child class instance
    # @param letype LeType : The wanted LeType child class (not instance !)
    # @param get_sub bool : If True, leo will be the superior and we wants all subordinates of Type letype, else its the oposite, leo is the subordinates and we want superiors with Type letype
    # @return a list of dict { 'id_relation':.., 'rank':.., 'lesup':.., 'lesub'.., 'rel_attrs': dict() }
    def get_related(self, leo, letype, get_sub=True):
        pass

    ## @brief Delete a relation between 2 LeType
    # @param lesup LeType
    # @param lesub LeType
    # @param fields dict
    # @return True if success else return False
    def del_related(self, lesup, lesub, fields=None):
        pass

    ## @brief Fetch a relation
    # @param id_relation int : The relation identifier
    # @return a dict{'id_relation':.., 'lesup':.., 'lesub':.., < if exists 'dict_attr':..>}
    def get_relation(self, id_relation, no_attr = False):
        pass

    ## @brief Fetch all relations concerning an object (rel2type relations)
    # @param leo LeType : LeType child instance
    # @return a list of tuple (lesup, lesub, dict_attr)
    def get_relations(self, leo):
        pass

    ## @brief Set the rank of a relation identified by its ID
    # @param id_relation int : relation ID
    # @param rank int|str : 'first', 'last', or an integer value
    def set_relation_rank(self, id_relation, rank):
        pass

    ## @brief Delete a relation between two LeType
    # @note It will deleted a relation in a rel2type between lesup.Class and lesub.Type
    # @param id_relation int : The relation identifier
    # @return True if deleted
    def del_relation(self, id_relation):
        pass
