# -*- coding: utf-8 -*-

""" Main object to manipulate Editorial Model
    parent of all other EM editing classes
    @see EmClass, EmType, EmFieldGroup, EmField
"""

from Lodel.utils.mlstring import MlString

class EmComponent(object):

    """ instaciate an EmComponent
        @param id_or_name int|str: name or id of the object
        @exception TypeError
    """
    def __init__(self, id_or_name):
        if self is EmComponent:
            raise EnvironmentError('Abstract class')
        if id_or_name is int:
            self.id = id_or_name
        elif id_or_name is str:
            self.name = id_or_name
            self.populate()
        else:
            raise TypeError('Bad argument: expecting <int> or <str>')

    """ Lookup in the database properties of the object to populate the properties
    """
    def populate(self):
        if self.id is None:
            where = "name = " + db.quote(self.name)
        else:
            where = "id = " + self.id

        row = db.query('*', self.table, where)
        if not row:
            # could have two possible Error message for id and for name
            raise EmComponentNotExistError("Bad id_or_name: could not find the component")

        self.name = row.name
        self.rank = int(row.rank)
        self.date_update = row.date_update
        self.date_create = row.date_create
        self.string = MlString.from_json(row.string)
        self.help = MlString.from_json(row.help)
        self.icon = row.icon

        return row

    """ write the representation of the component in the database
        @return bool
    """
    def save(self):
        pass

    """ delete this component data in the database
        @return bool
    """
    def delete(self):
        pass

    """ change the rank of the component
        @param int new_rank new position
    """
    def modify_rank(self, new_rank):
        pass

    """ set a string representation of the component for a given language
        @param  lang str: iso 639-2 code of the language http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes
        @param  text str: text to set
        @return bool
    """
    def set_string(self, lang, text):
        pass

    """ set the string representation of the component
        @param  ml_string  MlString: strings for all language
        @return bool
    """
    def set_strings(self, ml_string):
        pass

    """ get the string representation of the component for the given language
        @param  lang   str: iso 639-2 code of the language
        @return text   str: 
    """
    def get_string(self, lang):
        pass
