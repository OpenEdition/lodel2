# -*- coding: utf-8 -*-

object_uid = 'lodel_id'
object_em_class_id = 'class_id'
object_em_type_id = 'type_id'

relation_uid = 'id_relation'
relation_superior = 'superior'
relation_subordinate = 'subordinate'
relation_name = 'relation_name'


common_fields = {
    object_uid: {
        'fieldtype': 'pk',
        'internal': 'autosql',
    },
    object_em_class_id : {
        'fieldtype': 'emuid',
        'is_id_class': True,
        'internal': 'automatic',
    },
    object_em_type_id : {
        'fieldtype': 'emuid',
        'is_id_class': False,
        'internal': 'automatic',
    },
    'string': {
        'fieldtype': 'char',
        'max_length': 128,
        'internal': 'automatic',
        'nullable': True,
    },
    'creation_date': {
        'fieldtype': 'datetime',
        'now_on_create': True,
        'internal': 'autosql',
    },
    'modification_date': {
        'fieldtype': 'datetime',
        'now_on_create': True,
        'now_on_update': True,
        'internal': 'autosql',
    }
}

relations_common_fields = {
    relation_uid: {
        'fieldtype': 'pk',
        'internal': 'autosql',
    },
    'nature': {
        'fieldtype': 'naturerelation',
    },
    'depth': {
        'fieldtype': 'integer',
        'internal': 'automatic',
    },
    'rank': {
        'fieldtype': 'rank',
        'internal': 'automatic',
    },
    relation_superior : {
        'fieldtype': 'leo',
        'superior': True,
    },
    relation_subordinate: {
        'fieldtype': 'leo',
        'superior': False,
    },
    relation_name: {
        'fieldtype': 'char',
        'max_length': 128,
        'internal': 'automatic',
    }
}


def pk_name():
    for name, option in common_fields.items():
        if option['fieldtype'] == 'pk':
            return name


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
#   Classtypes contains default internal fields too
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
        'default_fields': {}
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
        'default_fields': {}
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
        'default_fields': {}
    }

    ## @brief return a classtype from its name
    # @param cls
    # @param classtype str : A classtype name
    # @return None if no classtype with this name, else return a dict containing classtype informations
    @classmethod
    def get(cls, classtype):
        try:
            return getattr(cls, classtype.lower())
        except AttributeError:
            return None

    ## @brief Get all the classtype
    # @return A list of dict representing classtypes
    @classmethod
    def getall(cls):
        return [cls.entity, cls.entry, cls.person]

    ## @brief Return possible nature of relations for a classtype name
    #
    # @param classtype_name str: The classtype name
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
