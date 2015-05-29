# -*- coding: utf-8 -*-

""" Manipulate Classes of the Editorial Model
    Create classes of object
    @see EmClass, EmType, EmFieldGroup, EmField
"""

from EditorialModel.components import EmComponent, EmComponentNotExistError
import EditorialModel.classtypes
from Database.sqlwrapper import SqlWrapper

class EmClass(EmComponent):
    def __init__(self, id_or_name):
        self.table = 'em_class'
        super(EmClass, self).__init__(id_or_name)

    """ create a new class
        @param name str: name of the new class
        @param class_type EmClasstype: type of the class
    """
    @staticmethod
    def create(name, class_type):
        #try:
        exists = EmClass(name)
        #except EmComponentNotExistError:
            #print ("bin")
            #pass
        print (name, class_type)
        pass

    """ retrieve list of the field_groups of this class
        @return field_groups [EmFieldGroup]:
    """
    def field_groups():
        pass

    """ retrieve list of fields
        @return fields [EmField]:
    """
    def fields():
        pass

    """ retrieve list of type of this class
        @return types [EmType]:
    """
    def types():
        pass

    """ add a new EmType that can ben linked to this class
        @param  t EmType: type to link
        @return success bool: done or not
    """
    def link_type(t):
        pass

    """ retrieve list of EmType that are linked to this class
        @return types [EmType]:
    """
    def linked_types():
        pass