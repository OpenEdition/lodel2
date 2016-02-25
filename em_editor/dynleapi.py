## @author LeFactory

import EditorialModel
from EditorialModel import fieldtypes
from EditorialModel.fieldtypes import pk, dictionary, integer, leo, rank, bool, char, emuid, datetime, namerelation, naturerelation, i18n
from Lodel.utils.mlstring import MlString

import leapi
import leapi.lecrud
import leapi.leobject
import leapi.lerelation
from leapi.leclass import _LeClass
from leapi.letype import _LeType

## @brief _LeCrud concret class
# @see leapi.lecrud._LeCrud
class LeCrud(leapi.lecrud._LeCrud):
    _uid_fieldtype = None

## @brief _LeObject concret class
# @see leapi.leobject._LeObject
class LeObject(LeCrud, leapi.leobject._LeObject):
    _me_uid = {1: '_Editorialmodel', 36: 'Classtype', 37: 'Hierarchyoptions', 38: 'Editorialmodel', 39: 'Emclass', 40: 'Emtype', 41: 'Emfield', 42: 'Emmodification', 15: '_Hierarchy', 8: '_Classtype', 22: 'Emcomponent', 29: '_Emmodification'}
    _me_uid_field_names = ('class_id', 'type_id')
    _uid_fieldtype = { 'lodel_id': EditorialModel.fieldtypes.pk.EmFieldType(**{'immutable': True, 'string': '{"___": "", "fre": "identifiant lodel", "eng": "lodel identifier"}', 'nullable': False, 'uniq': False, 'internal': 'autosql'}) }
    _leo_fieldtypes = {
	'class_id': EditorialModel.fieldtypes.emuid.EmFieldType(**{'immutable': True, 'is_id_class': True, 'string': '{"___": "", "fre": "identifiant de la classe", "eng": "class identifier"}', 'nullable': False, 'uniq': False, 'internal': 'automatic'}),
	'type_id': EditorialModel.fieldtypes.emuid.EmFieldType(**{'immutable': True, 'is_id_class': False, 'string': '{"___": "", "fre": "identifiant de la type", "eng": "type identifier"}', 'nullable': False, 'uniq': False, 'internal': 'automatic'}),
	'string': None,
	'creation_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'immutable': True, 'string': '{"___": "", "fre": "Date de création", "eng": "Creation date"}', 'now_on_create': True, 'nullable': False, 'uniq': False, 'internal': 'autosql'}),
	'modification_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'immutable': True, 'string': '{"___": "", "fre": "Date de modification", "eng": "Modification date"}', 'now_on_create': True, 'nullable': False, 'uniq': False, 'internal': 'autosql', 'now_on_update': True})
	}

## @brief _LeRelation concret class
# @see leapi.lerelation._LeRelation
class LeRelation(LeCrud, leapi.lerelation._LeRelation):
    _uid_fieldtype = { 'id_relation': EditorialModel.fieldtypes.pk.EmFieldType(**{'immutable': True, 'internal': 'autosql'}) }
    _rel_fieldtypes = {
	'depth': EditorialModel.fieldtypes.integer.EmFieldType(**{'immutable': True, 'internal': 'automatic'}),
	'subordinate': EditorialModel.fieldtypes.leo.EmFieldType(**{'immutable': True, 'superior': False}),
	'superior': EditorialModel.fieldtypes.leo.EmFieldType(**{'immutable': True, 'superior': True}),
	'relation_name': EditorialModel.fieldtypes.namerelation.EmFieldType(**{'immutable': True, 'max_length': 128}),
	'rank': EditorialModel.fieldtypes.rank.EmFieldType(**{'immutable': True, 'internal': 'automatic'}),
	'nature': EditorialModel.fieldtypes.naturerelation.EmFieldType(**{'immutable': True})
	}
    ## WARNING !!!! OBSOLETE ! DON'T USE IT
    _superior_field_name = 'superior'
    ## WARNING !!!! OBSOLETE ! DON'T USE IT
    _subordinate_field_name = 'subordinate'

class LeHierarch(LeRelation, leapi.lerelation._LeHierarch):
    pass

class LeRel2Type(LeRelation, leapi.lerelation._LeRel2Type):
    pass

class LeClass(LeObject, _LeClass):
    pass

class LeType(LeClass, _LeType):
    pass

## @brief EmClass _Editorialmodel LeClass child class
# @see leapi.leclass.LeClass
class _Editorialmodel(LeClass, LeObject):
    _class_id = 1
    ml_string = MlString('_EditorialModel')


## @brief EmClass _Classtype LeClass child class
# @see leapi.leclass.LeClass
class _Classtype(LeClass, LeObject):
    _class_id = 8
    ml_string = MlString('_ClassType')


## @brief EmClass _Hierarchy LeClass child class
# @see leapi.leclass.LeClass
class _Hierarchy(LeClass, LeObject):
    _class_id = 15
    ml_string = MlString('_Hierarchy')


## @brief EmClass Emcomponent LeClass child class
# @see leapi.leclass.LeClass
class Emcomponent(LeClass, LeObject):
    _class_id = 22
    ml_string = MlString('EmComponent')


## @brief EmClass _Emmodification LeClass child class
# @see leapi.leclass.LeClass
class _Emmodification(LeClass, LeObject):
    _class_id = 29
    ml_string = MlString('_EmModification')


## @brief EmType Classtype LeType child class
# @see leobject::letype::LeType
class Classtype(LeType, _Classtype):
    _type_id = 36
    ml_string = MlString('ClassType')


## @brief EmType Hierarchyoptions LeType child class
# @see leobject::letype::LeType
class Hierarchyoptions(LeType, _Hierarchy):
    _type_id = 37
    ml_string = MlString('HierarchyOptions')


## @brief EmType Editorialmodel LeType child class
# @see leobject::letype::LeType
class Editorialmodel(LeType, _Editorialmodel):
    _type_id = 38
    ml_string = MlString('EditorialModel')


## @brief EmType Emclass LeType child class
# @see leobject::letype::LeType
class Emclass(LeType, Emcomponent):
    _type_id = 39
    ml_string = MlString('EmClass')


## @brief EmType Emmodification LeType child class
# @see leobject::letype::LeType
class Emmodification(LeType, _Emmodification):
    _type_id = 42
    ml_string = MlString('EmModification')


## @brief EmType Emtype LeType child class
# @see leobject::letype::LeType
class Emtype(LeType, Emcomponent):
    _type_id = 40
    ml_string = MlString('EmType')


## @brief EmType Emfield LeType child class
# @see leobject::letype::LeType
class Emfield(LeType, Emcomponent):
    _type_id = 41
    ml_string = MlString('EmField')


class Rel_ClasstypeHierarchyoptionsHierarchy_Specs(LeRel2Type):
    _rel_attr_fieldtypes = {
    'nature': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': False, 'max_length': 10, 'internal': False})
}
    _superior_cls = _Classtype
    _subordinate_cls = Hierarchyoptions
    _relation_name = 'hierarchy_specs'


class RelEmcomponentClasstypeClasstype(LeRel2Type):
    _rel_attr_fieldtypes = {
}
    _superior_cls = Emcomponent
    _subordinate_cls = Classtype
    _relation_name = 'classtype'


class RelEmcomponentEmfieldSort_Column(LeRel2Type):
    _rel_attr_fieldtypes = {
}
    _superior_cls = Emcomponent
    _subordinate_cls = Emfield
    _relation_name = 'sort_column'


class RelEmcomponentEmclassParent_Class(LeRel2Type):
    _rel_attr_fieldtypes = {
}
    _superior_cls = Emcomponent
    _subordinate_cls = Emclass
    _relation_name = 'parent_class'


class RelEmcomponentEmfieldSelected_Field(LeRel2Type):
    _rel_attr_fieldtypes = {
}
    _superior_cls = Emcomponent
    _subordinate_cls = Emfield
    _relation_name = 'selected_field'


class RelEmcomponentEmtypeSuperiors(LeRel2Type):
    _rel_attr_fieldtypes = {
    'nature': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': False, 'max_length': 10, 'internal': False})
}
    _superior_cls = Emcomponent
    _subordinate_cls = Emtype
    _relation_name = 'superiors'


class RelEmcomponentEmfieldRel_Field(LeRel2Type):
    _rel_attr_fieldtypes = {
}
    _superior_cls = Emcomponent
    _subordinate_cls = Emfield
    _relation_name = 'rel_field'


#Initialisation of _Editorialmodel class attributes
_Editorialmodel._fieldtypes = {
    'description': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': False, 'max_length': 4096, 'internal': False}),
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'immutable': False, 'nullable': True, 'max_length': 128, 'internal': 'automatic', 'uniq': False}),
    'name': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': False, 'max_length': 56, 'internal': False})
}
_Editorialmodel.ml_fields_strings = {
   'class_id': MlString({"___": "class_id", "eng": "class identifier", "fre": "identifiant de la classe"}),
   'type_id': MlString({"___": "type_id", "eng": "type identifier", "fre": "identifiant de la type"}),
   'string': MlString({"___": "string", "eng": "String representation", "fre": "Repr\u00e9sentation textuel"}),
   'creation_date': MlString({"___": "creation_date", "eng": "Creation date", "fre": "Date de cr\u00e9ation"}),
   'lodel_id': MlString({"___": "lodel_id", "eng": "lodel identifier", "fre": "identifiant lodel"}),
   'name': MlString({"___": "name"}),
   'description': MlString({"___": "description"}),
   'modification_date': MlString({"___": "modification_date", "eng": "Modification date", "fre": "Date de modification"})
}
_Editorialmodel._linked_types = {
}
_Editorialmodel._classtype = 'entity'

#Initialisation of _Classtype class attributes
_Classtype._fieldtypes = {
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'immutable': False, 'nullable': True, 'max_length': 128, 'internal': 'automatic', 'uniq': False}),
    'name': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': False, 'max_length': 56, 'internal': False})
}
_Classtype.ml_fields_strings = {
   'class_id': MlString({"___": "class_id", "eng": "class identifier", "fre": "identifiant de la classe"}),
   'hierarchy_specs': MlString({"___": "hierarchy_specs"}),
   'nature': MlString({"___": "nature"}),
   'type_id': MlString({"___": "type_id", "eng": "type identifier", "fre": "identifiant de la type"}),
   'string': MlString({"___": "string", "eng": "String representation", "fre": "Repr\u00e9sentation textuel"}),
   'creation_date': MlString({"___": "creation_date", "eng": "Creation date", "fre": "Date de cr\u00e9ation"}),
   'lodel_id': MlString({"___": "lodel_id", "eng": "lodel identifier", "fre": "identifiant lodel"}),
   'name': MlString({"___": "name"}),
   'modification_date': MlString({"___": "modification_date", "eng": "Modification date", "fre": "Date de modification"})
}
_Classtype._linked_types = {
    'hierarchy_specs': Hierarchyoptions
}
_Classtype._classtype = 'entity'

#Initialisation of _Hierarchy class attributes
_Hierarchy._fieldtypes = {
    'automatic': EditorialModel.fieldtypes.bool.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': False}),
    'maxchildren': EditorialModel.fieldtypes.integer.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': False}),
    'maxdepth': EditorialModel.fieldtypes.integer.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': False}),
    'attach': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': False, 'max_length': 10, 'internal': False}),
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'immutable': False, 'nullable': True, 'max_length': 128, 'internal': 'automatic', 'uniq': False})
}
_Hierarchy.ml_fields_strings = {
   'class_id': MlString({"___": "class_id", "eng": "class identifier", "fre": "identifiant de la classe"}),
   'automatic': MlString({"___": "automatic"}),
   'maxdepth': MlString({"___": "maxdepth"}),
   'maxchildren': MlString({"___": "maxchildren"}),
   'type_id': MlString({"___": "type_id", "eng": "type identifier", "fre": "identifiant de la type"}),
   'string': MlString({"___": "string", "eng": "String representation", "fre": "Repr\u00e9sentation textuel"}),
   'creation_date': MlString({"___": "creation_date", "eng": "Creation date", "fre": "Date de cr\u00e9ation"}),
   'lodel_id': MlString({"___": "lodel_id", "eng": "lodel identifier", "fre": "identifiant lodel"}),
   'attach': MlString({"___": "attach"}),
   'modification_date': MlString({"___": "modification_date", "eng": "Modification date", "fre": "Date de modification"})
}
_Hierarchy._linked_types = {
}
_Hierarchy._classtype = 'entity'

#Initialisation of Emcomponent class attributes
Emcomponent._fieldtypes = {
    'date_update': EditorialModel.fieldtypes.datetime.EmFieldType(**{'now_on_update': True, 'nullable': False, 'uniq': False, 'internal': 'automatic'}),
    'fieldtype': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': False}),
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'immutable': False, 'nullable': True, 'max_length': 128, 'internal': 'automatic', 'uniq': False}),
    'name': EditorialModel.fieldtypes.char.EmFieldType(**{'uniq': False, 'nullable': False, 'max_length': 56, 'internal': False}),
    'help_text': EditorialModel.fieldtypes.i18n.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': False, 'default': {'en': 'no help'}}),
    'fieldtype_options': EditorialModel.fieldtypes.dictionary.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': False}),
    'date_create': EditorialModel.fieldtypes.datetime.EmFieldType(**{'uniq': False, 'nullable': False, 'internal': 'automatic', 'now_on_create': True})
}
Emcomponent.ml_fields_strings = {
   'class_id': MlString({"___": "class_id", "eng": "class identifier", "fre": "identifiant de la classe"}),
   'classtype': MlString({"___": "classtype"}),
   'rel_field': MlString({"___": "rel_field"}),
   'superiors': MlString({"___": "superiors"}),
   'string': MlString({"___": "string", "eng": "String representation", "fre": "Repr\u00e9sentation textuel"}),
   'type_id': MlString({"___": "type_id", "eng": "type identifier", "fre": "identifiant de la type"}),
   'fieldtype': MlString({"___": "fieldtype"}),
   'creation_date': MlString({"___": "creation_date", "eng": "Creation date", "fre": "Date de cr\u00e9ation"}),
   'selected_field': MlString({"___": "selected_field"}),
   'fieldtype_options': MlString({"___": "fieldtype_options"}),
   'date_create': MlString({"___": "date_create"}),
   'date_update': MlString({"___": "date_update"}),
   'modification_date': MlString({"___": "modification_date", "eng": "Modification date", "fre": "Date de modification"}),
   'name': MlString({"___": "name"}),
   'lodel_id': MlString({"___": "lodel_id", "eng": "lodel identifier", "fre": "identifiant lodel"}),
   'sort_column': MlString({"___": "sort_column"}),
   'help_text': MlString({"___": "help_text"}),
   'parent_class': MlString({"___": "parent_class"}),
   'nature': MlString({"___": "nature"})
}
Emcomponent._linked_types = {
    'classtype': Classtype,
    'superiors': Emtype,
    'rel_field': Emfield,
    'sort_column': Emfield,
    'selected_field': Emfield,
    'parent_class': Emclass
}
Emcomponent._classtype = 'entity'

#Initialisation of _Emmodification class attributes
_Emmodification._fieldtypes = {
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'immutable': False, 'nullable': True, 'max_length': 128, 'internal': 'automatic', 'uniq': False})
}
_Emmodification.ml_fields_strings = {
   'class_id': MlString({"___": "class_id", "eng": "class identifier", "fre": "identifiant de la classe"}),
   'type_id': MlString({"___": "type_id", "eng": "type identifier", "fre": "identifiant de la type"}),
   'string': MlString({"___": "string", "eng": "String representation", "fre": "Repr\u00e9sentation textuel"}),
   'creation_date': MlString({"___": "creation_date", "eng": "Creation date", "fre": "Date de cr\u00e9ation"}),
   'lodel_id': MlString({"___": "lodel_id", "eng": "lodel identifier", "fre": "identifiant lodel"}),
   'modification_date': MlString({"___": "modification_date", "eng": "Modification date", "fre": "Date de modification"})
}
_Emmodification._linked_types = {
}
_Emmodification._classtype = 'entity'

#Initialisation of Classtype class attributes
Classtype._fields = ['name']
Classtype._superiors = {}
Classtype._leclass = _Classtype

#Initialisation of Hierarchyoptions class attributes
Hierarchyoptions._fields = ['attach', 'automatic', 'maxdepth', 'maxchildren']
Hierarchyoptions._superiors = {}
Hierarchyoptions._leclass = _Hierarchy

#Initialisation of Editorialmodel class attributes
Editorialmodel._fields = ['name', 'description']
Editorialmodel._superiors = {}
Editorialmodel._leclass = _Editorialmodel

#Initialisation of Emclass class attributes
Emclass._fields = ['name', 'help_text', 'date_update', 'date_create']
Emclass._superiors = {'parent': [Editorialmodel]}
Emclass._leclass = Emcomponent

#Initialisation of Emmodification class attributes
Emmodification._fields = []
Emmodification._superiors = {}
Emmodification._leclass = _Emmodification

#Initialisation of Emtype class attributes
Emtype._fields = ['name', 'help_text', 'date_update', 'date_create']
Emtype._superiors = {'parent': [Emclass]}
Emtype._leclass = Emcomponent

#Initialisation of Emfield class attributes
Emfield._fields = ['name', 'help_text', 'date_update', 'date_create', 'fieldtype', 'fieldtype_options']
Emfield._superiors = {'parent': [Emtype]}
Emfield._leclass = Emcomponent

## @brief Dict for getting LeClass and LeType child classes given an EM uid
LeObject._me_uid = {1: _Editorialmodel, 36: Classtype, 37: Hierarchyoptions, 38: Editorialmodel, 39: Emclass, 40: Emtype, 41: Emfield, 42: Emmodification, 15: _Hierarchy, 8: _Classtype, 22: Emcomponent, 29: _Emmodification}
