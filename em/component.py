# -*- coding: utf-8 -*-

## Main object to manipulate Editorial Model
#
# parent of all other EM editing classes
# @see EmClass, EmType, EmFieldGroup, EmField

class EmComponent(object):

    ## instaciate an EmComponent
    # @param id_or_name <int> || <str>
    # @raise TypeError
    def __init(id_or_name):
        if id_or_name is int:
            self.id = id_or_name
        else if id_or_name is str:
            self.name = id_or_name
            self.populate()
        else:
            raise TypeError('Bad argument: expecting <int> or <str>')

    ## Lookup in the database properties of the object
    def populate(self):
        if self.id is None:
            where = "name = " + db.quote(self.name)
        else:
            where = "id = " + self.id
        
        row = db.query(where)
        if not row:
            # could have two possible Error message for id and for name
            raise EmComponentNotExistError("Bad id_or_name: could not find the component")
        
        self.name = row.name
        self.rank = row.rank
        self.date_update = row.date_update
        self.date_create <datetime object>
        self.string <MlString object> : string representation of the component
        self.help <MlString object> : help string
        self.icon <string> : path to the icon (should be id_global of EmFile object)

    @static_method
    def id_from_name(name):

    @staticmethod
    def create(name <string>, parent_component <EmComponent object>) 
    def save(self)
    def delete(self)
    def modify_rank(self)
    def set_string(self, lang, texte)
    def set_strings(self)
    def get_string(self, lang)
