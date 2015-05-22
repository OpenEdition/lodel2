# -*- coding: utf-8 -*-

## Manipulate Classes of the Editorial Model
#
# Create classes of object
# @see EmClass, EmType, EmFieldGroup, EmField

import EmComponent

class EmClass(EmComponent)
    def __init(id_or_name):
        self.table = 'em_class'
        pass

    ## create a new class
    # @param str         name       name of the new class
    # @param EmClasstype class_type type of the class
    def create(self, name, class_type):
       pass

    ## retrieve list field_groups of this class
    # @return [EmFieldGroup]
    def field_groups():
       pass

    def fields():
       pass

    def types():
        pass

    ## add a new EmType that can ben linked to this class
    # @param  EmType t       type to link
    # @return bool   success
    def link_type(t <EmType>):
        pass
    
    ## retrieve list of EmType that are linked to this class
    # @return [EmType]
    def linked_types():
        pass