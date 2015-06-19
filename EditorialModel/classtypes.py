# -*- coding: utf-8 -*-

## constant name for the nature of type hierarchy
class EmNature(object):
    PARENT = 'parent'
    TRANSLATION = 'translation'
    IDENTITY = 'identity'

##  Representation of the classTypes
#
#    Defines 3 generic classtype : entity, entry and person
#        - entity : to define editorial content
#        - entry  : to define keywords
#        - person : to define people (in the real world, this classtype will only have one class and one type)
#
#    The hierarchy dict fixes the possible hierarchical links the types of each classtype can have :
#       - 'attach' : what type of superior a type can have
#            - 'classtype' a type can have superiors of the same classtype
#            - 'type'      a type can only have superiors of the same type
#       - automatic : possible superiors 
#            - False : possible superiors must be defined
#            - True  : possible superiors can not be defined, they will be enforced by the ME automatically
#       - maxdepth : maximum depth
#       - maxchildren : maximum children
#
class EmClassType(object):

    entity = {
        'name' : 'entity',
        'hierarchy' : {
            EmNature.PARENT : {
                'attach'   : 'classtype',
                'automatic' : False,
                'maxdepth' : -1,
                'maxchildren' : -1
                },
            EmNature.TRANSLATION : {
                'attach'   : 'type',
                'automatic' : False,
                'maxdepth' : 1,
                'maxchildren' : -1
                },
        },
    }

    entry = {
        'name' : 'entry',
        'hierarchy' : {
            EmNature.PARENT : {
                'attach'   : 'type',
                'automatic' : False,
                },
            EmNature.TRANSLATION : {
                'attach'   : 'type',
                'automatic' : False,
                'maxdepth' : 1,
                'maxchildren' : -1
                },
        },
    }

    person = {
        'name' : 'person',
        'hierarchy' : {
            EmNature.IDENTITY : {
                'attach'   : 'classtype',
                'automatic' : True,
                'maxdepth' : -1,
                'maxchildren' : 1
            },
        },
    }
