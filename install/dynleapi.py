## @author LeFactory

import EditorialModel
from EditorialModel import fieldtypes
from EditorialModel.fieldtypes import naturerelation, char, integer, datetime, pk

import leapi
import leapi.lecrud
import leapi.leobject
import leapi.lerelation
from leapi.leclass import _LeClass
from leapi.letype import _LeType

import DataSource.MySQL.leapidatasource


## @brief _LeCrud concret class
# @see leapi.lecrud._LeCrud
class LeCrud(leapi.lecrud._LeCrud):
    _datasource = DataSource.MySQL.leapidatasource.LeDataSourceSQL(**{})
    _uid_fieldtype = None

## @brief _LeObject concret class
# @see leapi.leobject._LeObject
class LeObject(LeCrud, leapi.leobject._LeObject):
    _me_uid = {1: 'Textes', 2: 'Personnes', 19: 'Numero', 5: 'Article', 6: 'Personne', 13: 'Publication', 14: 'Rubrique'}
    _uid_fieldtype = { 'lodel_id': EditorialModel.fieldtypes.pk.EmFieldType(**{'internal': 'automatic'}) }
    _leo_fieldtypes = {
	'creation_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'now_on_create': True, 'internal': 'automatic'}),
	'string': EditorialModel.fieldtypes.char.EmFieldType(**{'max_length': 128, 'internal': 'automatic'}),
	'modification_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'now_on_update': True, 'now_on_create': True, 'internal': 'automatic'}),
	'type_id': EditorialModel.fieldtypes.integer.EmFieldType(**{'internal': 'automatic'}),
	'class_id': EditorialModel.fieldtypes.integer.EmFieldType(**{'internal': 'automatic'})
	}

## @brief _LeRelation concret class
# @see leapi.lerelation._LeRelation
class LeRelation(LeCrud, leapi.lerelation._LeRelation):
    _uid_fieldtype = { 'id_relation': EditorialModel.fieldtypes.pk.EmFieldType(**{'internal': 'automatic'}) }
    _rel_fieldtypes = {
	'rank': EditorialModel.fieldtypes.integer.EmFieldType(**{'internal': 'automatic'}),
	'nature': EditorialModel.fieldtypes.naturerelation.EmFieldType(**{}),
	'depth': EditorialModel.fieldtypes.integer.EmFieldType(**{'internal': 'automatic'})
	}
    _rel_attr_fieldtypes = dict()

class LeHierarch(LeRelation, leapi.lerelation._LeHierarch):
    _rel_attr_fieldtypes = dict()

class LeRel2Type(LeRelation, leapi.lerelation._LeRel2Type):
    pass

class LeClass(LeObject, _LeClass):
    pass

class LeType(LeClass, _LeType):
    pass

## @brief EmClass Textes LeClass child class
# @see leapi.leclass.LeClass
class Textes(LeClass, LeObject):
    _class_id = 1


## @brief EmClass Personnes LeClass child class
# @see leapi.leclass.LeClass
class Personnes(LeClass, LeObject):
    _class_id = 2


## @brief EmClass Publication LeClass child class
# @see leapi.leclass.LeClass
class Publication(LeClass, LeObject):
    _class_id = 13


## @brief EmType Article LeType child class
# @see leobject::letype::LeType
class Article(LeType, Textes):
    _type_id = 5


## @brief EmType Personne LeType child class
# @see leobject::letype::LeType
class Personne(LeType, Personnes):
    _type_id = 6


## @brief EmType Rubrique LeType child class
# @see leobject::letype::LeType
class Rubrique(LeType, Publication):
    _type_id = 14


## @brief EmType Numero LeType child class
# @see leobject::letype::LeType
class Numero(LeType, Publication):
    _type_id = 19


class Rel_textes2personne(LeRel2Type):
    _rel_attr_fieldtypes = {
    'adresse': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': True, 'internal': False})
}


#Initialisation of Textes class attributes
Textes._fieldtypes = {
    'modification_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'nullable': False, 'uniq': False, 'now_on_update': True, 'now_on_create': True, 'internal': 'automatic'}),
    'soustitre': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': True, 'internal': False}),
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'nullable': True, 'uniq': False, 'max_length': 128, 'internal': 'automatic'}),
    'titre': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': True, 'internal': False}),
    'bleu': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': True, 'internal': False}),
    'lodel_id': EditorialModel.fieldtypes.pk.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': 'automatic'}),
    'type_id': EditorialModel.fieldtypes.integer.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': 'automatic'}),
    'class_id': EditorialModel.fieldtypes.integer.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': 'automatic'}),
    'creation_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'uniq': False, 'nullable': False, 'now_on_create': True, 'internal': 'automatic'})
}
Textes._linked_types = [Personne]
Textes._classtype = 'entity'

#Initialisation of Personnes class attributes
Personnes._fieldtypes = {
    'nom': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': True, 'internal': False}),
    'age': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': True, 'internal': False}),
    'prenom': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': True, 'internal': False}),
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'nullable': True, 'uniq': False, 'max_length': 128, 'internal': 'automatic'}),
    'lodel_id': EditorialModel.fieldtypes.pk.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': 'automatic'}),
    'modification_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'nullable': False, 'uniq': False, 'now_on_update': True, 'now_on_create': True, 'internal': 'automatic'}),
    'type_id': EditorialModel.fieldtypes.integer.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': 'automatic'}),
    'class_id': EditorialModel.fieldtypes.integer.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': 'automatic'}),
    'creation_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'uniq': False, 'nullable': False, 'now_on_create': True, 'internal': 'automatic'})
}
Personnes._linked_types = []
Personnes._classtype = 'person'

#Initialisation of Publication class attributes
Publication._fieldtypes = {
    'modification_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'nullable': False, 'uniq': False, 'now_on_update': True, 'now_on_create': True, 'internal': 'automatic'}),
    'creation_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'uniq': False, 'nullable': False, 'now_on_create': True, 'internal': 'automatic'}),
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'nullable': True, 'uniq': False, 'max_length': 128, 'internal': 'automatic'}),
    'lodel_id': EditorialModel.fieldtypes.pk.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': 'automatic'}),
    'titre': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': True, 'internal': False}),
    'type_id': EditorialModel.fieldtypes.integer.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': 'automatic'}),
    'class_id': EditorialModel.fieldtypes.integer.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': 'automatic'})
}
Publication._linked_types = []
Publication._classtype = 'entity'

#Initialisation of Article class attributes
Article._fields = ['titre', 'class_id', 'soustitre', 'string', 'type_id', 'lodel_id', 'modification_date', 'creation_date']
Article._superiors = {'parent': [Rubrique]}
Article._leclass = Textes

#Initialisation of Personne class attributes
Personne._fields = ['nom', 'class_id', 'prenom', 'string', 'type_id', 'lodel_id', 'modification_date', 'creation_date']
Personne._superiors = {}
Personne._leclass = Personnes

#Initialisation of Rubrique class attributes
Rubrique._fields = ['titre', 'class_id', 'string', 'type_id', 'lodel_id', 'modification_date', 'creation_date']
Rubrique._superiors = {'parent': [Rubrique, Numero]}
Rubrique._leclass = Publication

#Initialisation of Numero class attributes
Numero._fields = ['titre', 'class_id', 'string', 'type_id', 'lodel_id', 'modification_date', 'creation_date']
Numero._superiors = {}
Numero._leclass = Publication

## @brief Dict for getting LeClass and LeType child classes given an EM uid
LeObject._me_uid = {1: Textes, 2: Personnes, 19: Numero, 5: Article, 6: Personne, 13: Publication, 14: Rubrique}
