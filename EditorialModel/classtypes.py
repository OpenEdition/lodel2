# -*- coding: utf-8 -*-


## EmNature (Class)
#
# constant name for the nature of type hierarchy
class EmNature(object):
    PARENT = 'parent'
    TRANSLATION = 'translation'
    IDENTITY = 'identity'

    @classmethod
    def getall(cls):
        return [cls.PARENT, cls.TRANSLATION, cls.IDENTITY]


## EmClassType (Class)
#
# Representation of the classTypes
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
        'name': 'entity',
        'hierarchy': {
            EmNature.PARENT: {
                'attach': 'classtype',
                'automatic': False,
                'maxdepth': -1,
                'maxchildren': -1
            },
            EmNature.TRANSLATION: {
                'attach': 'type',
                'automatic': False,
                'maxdepth': 1,
                'maxchildren': -1
            },
        },
    }

    entry = {
        'name': 'entry',
        'hierarchy': {
            EmNature.PARENT: {
                'attach': 'type',
                'automatic': False,
            },
            EmNature.TRANSLATION: {
                'attach': 'type',
                'automatic': False,
                'maxdepth': 1,
                'maxchildren': -1
            },
        },
    }

    person = {
        'name': 'person',
        'hierarchy': {
            EmNature.IDENTITY: {
                'attach': 'classtype',
                'automatic': True,
                'maxdepth': -1,
                'maxchildren': 1
            },
        },
    }

    @classmethod
    def getall(cls):
        return [cls.entity, cls.entry, cls.person]

    ## natures (Method)
    #
    # Return possible nature of relations for a classtype name
    #
    # @param classtype str: The classtype name
    # @return A list of EmNature names (list of str)
    @staticmethod
    def natures(classtype_name):
        if not isinstance(classtype_name, str):
            raise TypeError("Excepted <class str> but got %s" % str(type(classtype_name)))
        try:
            classtype = getattr(EmClassType, classtype_name)
        except AttributeError:
            raise AttributeError("Unknown classtype : '%s'" % classtype_name)
        return classtype['hierarchy'].keys()
