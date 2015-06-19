#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent, EmComponentNotExistError
from Database import sqlutils
import sqlalchemy as sql

from EditorialModel.fieldgroups import EmFieldGroup
import EditorialModel.fieldtypes as ftypes
import EditorialModel.classes

## Represents type of documents
# A type is a specialisation of a class, it can select optional field,
# they have hooks, are organized in hierarchy and linked to other
# EmType with special fields called relation_to_type fields
#
# @see EditorialModel::components::EmComponent
class EmType(EmComponent):
    table = 'em_type'

    ## @brief Specific EmClass fields
    # @see EditorialModel::components::EmComponent::_fields
    _fields = [
        ('class_id', ftypes.EmField_integer),
        ('icon', ftypes.EmField_integer),
        ('sortcolumn', ftypes.EmField_char)
        ]

    @classmethod
    ## Create a new EmType and instanciate it
    # @param name str: The name of the new type
    # @param em_class EmClass: The class that the new type will specialize
    # @return An EmType instance
    #
    # @see EmComponent::__init__()
    # 
    # @todo Remove hardcoded default value for icon
    # @todo check that em_class is an EmClass object
    def create(c, name, em_class):
        try:
            exists = EmType(name)
        except EmComponentNotExistError:
            return super(EmType, c).create(name=name, class_id=em_class.uid, icon=0)

        return exists
    
    ## Get the list of associated fieldgroups
    # @return A list of EmFieldGroup uid
    def field_groups(self):
        fg_table = sqlutils.getTable(EmFieldGroup)
        req = fg_table.select(fg_table.c.uid).where(fg_table.c.class_id == self.class_id)
        conn = self.__class__.getDbE().connect()
        res = conn.execute(req)
        rows = res.fetchall()
        conn.close()

        return [ row['uid'] for row in rows ]

    ## Get the list of associated fields
    # @return A list of EmField uid
    def fields(self):
        res = []
        for fguid in self.field_groups():
            res += EmFieldGroup(fguid).fields()
        return res
        pass

    ## Indicate that an optionnal field is used
    # @param field EmField: The optional field to select
    # @throw TypeError if field is not an EmField
    # @throw ValueError if field is not an optionnal field
    def select_field(self, field):
        pass

    ## Indicate that an optionnal field will not be used (anymore)
    # @param field EmField: The optionnal field to unselect
    # @throw TypeError if field is not an EmField
    # @throw ValueError if field is not an optionnal field
    def unselect_field(self, field):
        pass

    ## Get the list of associated hooks
    # @note Not conceptualized yet
    # @todo Conception
    def hooks(self):
        pass

    ## Add a new hook
    # @param hook EmHook: An EmHook instance
    # @throw TypeError
    # @note Not conceptualized yet
    # @todo Conception
    def add_hook(self, hook):
        pass

    ## Delete a hook
    # @param hook EmHook: An EmHook instance
    # @throw TypeError
    # @note Not conceptualized yet
    # @todo Conception
    # @todo Maybe we don't need a EmHook instance but just a hook identifier
    def del_hook(self,hook):
        pass


    ## Get the list of superiors EmType in the type hierarchy
    # @return A list of EmType
    def superiors(self):
        pass


    ## Add a superior in the type hierarchy
    # @param em_type EmType: An EmType instance
    # @param relation_nature str: The name of the relation's nature
    # @throw TypeError when em_type not an EmType instance
    # @throw ValueError when relation_nature isn't reconized or not allowed for this type
    # @todo define return value and raise condition
    def add_superior(self, em_type, relation_nature):
        pass

    ## Delete a superior in the type hierarchy
    # @param em_type EmType: An EmType instance
    # @throw TypeError when em_type isn't an EmType instance
    # @todo define return value and raise condition
    def del_superior(self, em_type):
        pass

    ## @brief Get the list of linked type
    # Types are linked with special fields called relation_to_type fields
    # @return a list of EmType
    # @see EmFields
    def linked_types(self):
        pass
