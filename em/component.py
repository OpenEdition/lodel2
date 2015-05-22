# -*- coding: utf-8 -*-

## Main object to manipulate Editorial Model
#
# parent of all other EM editing classes
# @see EmClass, EmType, EmFieldGroup, EmField

class EmComponent(object):

    ## instaciate an EmComponent
    # @param int|str id_or_name 
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
        self.date_create = row.date_create
        self.string <MlString object> : string representation of the component
        self.help <MlString object> : help string
        self.icon <string> : path to the icon (should be id_global of EmFile object)

    ## write the representation of the component in the database
    # @return bool
    def save(self):
        pass

    ## delete this component in the database
    # @return bool
    def delete(self):
        pass

    ## change the rank of the component
    # @param int new_rank new position
    def modify_rank(self, new_rank):
        pass

    ## set a string representation of the component for a given language
    # @param  str lang iso 639-2 representation of the language http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes
    # @param  str text
    # @return bool
    def set_string(self, lang, text):
        pass

    ## set the string representation of the component
    # @param  MlString ml_string strings for all language
    # @return bool
    def set_strings(self, ml_string):
        pass

    ## get the string representation of the component for the given language
    # @param  str lang iso 639-2 representation of the language
    # @return str
    def get_string(self, lang):
        pass
