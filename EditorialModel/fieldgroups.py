#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from EditorialModel.classes import EmClass
import EditorialModel.fieldtypes as ftypes

from Database import sqlutils
import sqlalchemy as sql

import EditorialModel

## Represents groups of EmField associated with an EmClass
#
# EmClass fields representation is organised with EmFieldGroup
# @see EditorialModel::fields::EmField EditorialModel::classes::EmClass
class EmFieldGroup(EmComponent):

    ## The database table name
    table = 'em_fieldgroup'
    ## List of fields
    # @todo Bad storage, here we want an ordereddict not a tuple list
    _fields = [('class_id', ftypes.EmField_integer())]
    
    ## Instanciate an EmFieldGroup with data fetched from db
    # @param id_or_name str|int: Identify the EmFieldGroup by name or by global_id
    # @throw TypeError
    # @see EditorialModel::components::EmComponent::__init__()
    # @throw EditorialModel::components::EmComponentNotExistError

    @classmethod
    ## Create a new EmFieldGroup
    #
    # Save it in database and return an instance*
    # @param name str: The name of the new EmFieldGroup
    # @param em_class EmClass|str|int : Can be an EditorialModel::classes::EmClass uid, name or instance
    # @throw ValueError If an EmFieldGroup with this name allready exists
    # @throw ValueError If the specified EmClass don't exists
    # @throw TypeError If an argument is of an unexepted type
    def create(c, name, em_class):
        if not isinstance(em_class, EmClass):
            if isinstance(em_class, int) or isinstance(em_class, str):
                try:
                    arg = em_class
                    em_class = EmClass(arg)
                except EmComponentNotExistError:
                    raise ValueError("No EmClass found with id or name '"+arg+"'")
            else:
                raise TypeError("Excepting an EmClass, an int or a str for 'em_class' argument. Not an "+str(type(em_class))+".")

        if not isinstance(name, str):
            raise TypeError("Excepting a string as first argument, not an "+str(type(name)))

        try:
            exists = EmFieldGroup(name)
            raise ValueError("An EmFieldgroup named "+name+" allready exist")
        except EmComponentNotExistError:
            return super(EmFieldGroup, c).create(name=name, class_id = em_class.uid) #Check the return value ?

        return exists

    ## Get the list of associated fields
    # @return A list of EmField instance
    # @todo Implement this method
    def fields(self):
        field_table = sqlutils.getTable(EmField)
        req = field_table.select(field_table.c.uid).where(field_table.c.fieldgroup_id == self.uid)
        conn = self.__class__.getDbE().connect()
        res = conn.execute(req)
        rows = res.fetchall()
        conn.close()
        return [ EmField(row['uid']) for row in rows]

