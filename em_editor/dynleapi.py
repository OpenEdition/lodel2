## @author LeFactory

import EditorialModel
from EditorialModel import fieldtypes
from EditorialModel.fieldtypes import naturerelation, leo, datetime, dictionary, rank, namerelation, pk, bool, i18n, char, integer, emuid
from Lodel.utils.mlstring import MlString

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
    _me_uid = {32: 'Emclass', 33: 'Emtype', 34: 'Emfield', 22: 'Emcomponent', 1: '_Editorialmodel', 8: '_Classtype', 15: '_Hierarchy', 29: 'Classtype', 30: 'Hierarchyoptions', 31: 'Editorialmodel'}
    _me_uid_field_names = ('class_id', 'type_id')
    _uid_fieldtype = { 'lodel_id': EditorialModel.fieldtypes.pk.EmFieldType(**{'uniq': False, 'nullable': False, 'immutable': True, 'internal': 'autosql', 'string': '{"___": "", "fre": "identifiant lodel", "eng": "lodel identifier"}'}) }
    _leo_fieldtypes = {
	'class_id': EditorialModel.fieldtypes.emuid.EmFieldType(**{'uniq': False, 'nullable': False, 'immutable': True, 'internal': 'automatic', 'string': '{"___": "", "fre": "identifiant de la classe", "eng": "class identifier"}', 'is_id_class': True}),
	'type_id': EditorialModel.fieldtypes.emuid.EmFieldType(**{'uniq': False, 'nullable': False, 'immutable': True, 'internal': 'automatic', 'string': '{"___": "", "fre": "identifiant de la type", "eng": "type identifier"}', 'is_id_class': False}),
	'modification_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'uniq': False, 'internal': 'autosql', 'now_on_update': True, 'immutable': True, 'nullable': False, 'now_on_create': True, 'string': '{"___": "", "fre": "Date de modification", "eng": "Modification date"}'}),
	'string': None,
	'creation_date': EditorialModel.fieldtypes.datetime.EmFieldType(**{'uniq': False, 'internal': 'autosql', 'now_on_create': True, 'immutable': True, 'nullable': False, 'string': '{"___": "", "fre": "Date de création", "eng": "Creation date"}'})
	}

## @brief _LeRelation concret class
# @see leapi.lerelation._LeRelation
class LeRelation(LeCrud, leapi.lerelation._LeRelation):
    _uid_fieldtype = { 'id_relation': EditorialModel.fieldtypes.pk.EmFieldType(**{'immutable': True, 'internal': 'autosql'}) }
    _rel_fieldtypes = {
	'relation_name': EditorialModel.fieldtypes.namerelation.EmFieldType(**{'max_length': 128, 'immutable': True}),
	'nature': EditorialModel.fieldtypes.naturerelation.EmFieldType(**{'immutable': True}),
	'superior': EditorialModel.fieldtypes.leo.EmFieldType(**{'immutable': True, 'superior': True}),
	'depth': EditorialModel.fieldtypes.integer.EmFieldType(**{'immutable': True, 'internal': 'automatic'}),
	'rank': EditorialModel.fieldtypes.rank.EmFieldType(**{'immutable': True, 'internal': 'automatic'}),
	'subordinate': EditorialModel.fieldtypes.leo.EmFieldType(**{'immutable': True, 'superior': False})
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


## @brief EmType Classtype LeType child class
# @see leobject::letype::LeType
class Classtype(LeType, _Classtype):
    _type_id = 29
    ml_string = MlString('ClassType')


## @brief EmType Hierarchyoptions LeType child class
# @see leobject::letype::LeType
class Hierarchyoptions(LeType, _Hierarchy):
    _type_id = 30
    ml_string = MlString('HierarchyOptions')


## @brief EmType Editorialmodel LeType child class
# @see leobject::letype::LeType
class Editorialmodel(LeType, _Editorialmodel):
    _type_id = 31
    ml_string = MlString('EditorialModel')


## @brief EmType Emclass LeType child class
# @see leobject::letype::LeType
class Emclass(LeType, Emcomponent):
    _type_id = 32
    ml_string = MlString('EmClass')


## @brief EmType Emtype LeType child class
# @see leobject::letype::LeType
class Emtype(LeType, Emcomponent):
    _type_id = 33
    ml_string = MlString('EmType')


## @brief EmType Emfield LeType child class
# @see leobject::letype::LeType
class Emfield(LeType, Emcomponent):
    _type_id = 34
    ml_string = MlString('EmField')


class Rel_ClasstypeHierarchyoptionsHierarchy_Specs(LeRel2Type):
    _rel_attr_fieldtypes = {
    'nature': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': False, 'max_length': 10, 'uniq': False, 'nullable': False})
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
    'nature': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': False, 'max_length': '10', 'uniq': False, 'nullable': False})
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
    'description': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': False, 'max_length': 4096, 'uniq': False, 'nullable': False}),
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': 'automatic', 'max_length': 128, 'immutable': False, 'uniq': False, 'nullable': True}),
    'name': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': False, 'max_length': 56, 'uniq': False, 'nullable': False})
}
_Editorialmodel.ml_fields_strings = {
   'class_id': MlString({"___": "class_id", "eng": "class identifier", "fre": "identifiant de la classe"}),
   'type_id': MlString({"___": "type_id", "eng": "type identifier", "fre": "identifiant de la type"}),
   'name': MlString({"___": "name"}),
   'lodel_id': MlString({"___": "lodel_id", "eng": "lodel identifier", "fre": "identifiant lodel"}),
   'modification_date': MlString({"___": "modification_date", "eng": "Modification date", "fre": "Date de modification"}),
   'string': MlString({"___": "string", "eng": "String representation", "fre": "Repr\u00e9sentation textuel"}),
   'creation_date': MlString({"___": "creation_date", "eng": "Creation date", "fre": "Date de cr\u00e9ation"}),
   'description': MlString({"___": "description"})
}
_Editorialmodel._linked_types = {
}
_Editorialmodel._classtype = 'entity'

#Initialisation of _Classtype class attributes
_Classtype._fieldtypes = {
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': 'automatic', 'max_length': 128, 'immutable': False, 'uniq': False, 'nullable': True}),
    'name': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': False, 'max_length': 56, 'uniq': False, 'nullable': False})
}
_Classtype.ml_fields_strings = {
   'class_id': MlString({"___": "class_id", "eng": "class identifier", "fre": "identifiant de la classe"}),
   'type_id': MlString({"___": "type_id", "eng": "type identifier", "fre": "identifiant de la type"}),
   'name': MlString({"___": "name"}),
   'lodel_id': MlString({"___": "lodel_id", "eng": "lodel identifier", "fre": "identifiant lodel"}),
   'modification_date': MlString({"___": "modification_date", "eng": "Modification date", "fre": "Date de modification"}),
   'string': MlString({"___": "string", "eng": "String representation", "fre": "Repr\u00e9sentation textuel"}),
   'creation_date': MlString({"___": "creation_date", "eng": "Creation date", "fre": "Date de cr\u00e9ation"}),
   'hierarchy_specs': MlString({"___": "hierarchy_specs"}),
   'nature': MlString({"___": "nature"})
}
_Classtype._linked_types = {
    'hierarchy_specs': Hierarchyoptions
}
_Classtype._classtype = 'entity'

#Initialisation of _Hierarchy class attributes
_Hierarchy._fieldtypes = {
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': 'automatic', 'max_length': 128, 'immutable': False, 'uniq': False, 'nullable': True}),
    'attach': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': False, 'max_length': 10, 'uniq': False, 'nullable': False}),
    'maxdepth': EditorialModel.fieldtypes.integer.EmFieldType(**{'internal': False, 'uniq': False, 'nullable': False}),
    'maxchildren': EditorialModel.fieldtypes.integer.EmFieldType(**{'internal': False, 'uniq': False, 'nullable': False}),
    'automatic': EditorialModel.fieldtypes.bool.EmFieldType(**{'internal': False, 'uniq': False, 'nullable': False})
}
_Hierarchy.ml_fields_strings = {
   'maxchildren': MlString({"___": "maxchildren"}),
   'class_id': MlString({"___": "class_id", "eng": "class identifier", "fre": "identifiant de la classe"}),
   'type_id': MlString({"___": "type_id", "eng": "type identifier", "fre": "identifiant de la type"}),
   'lodel_id': MlString({"___": "lodel_id", "eng": "lodel identifier", "fre": "identifiant lodel"}),
   'modification_date': MlString({"___": "modification_date", "eng": "Modification date", "fre": "Date de modification"}),
   'automatic': MlString({"___": "automatic"}),
   'string': MlString({"___": "string", "eng": "String representation", "fre": "Repr\u00e9sentation textuel"}),
   'creation_date': MlString({"___": "creation_date", "eng": "Creation date", "fre": "Date de cr\u00e9ation"}),
   'attach': MlString({"___": "attach"}),
   'maxdepth': MlString({"___": "maxdepth"})
}
_Hierarchy._linked_types = {
}
_Hierarchy._classtype = 'entity'

#Initialisation of Emcomponent class attributes
Emcomponent._fieldtypes = {
    'fieldtype': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': False, 'uniq': False, 'nullable': False}),
    'name': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': False, 'max_length': 56, 'uniq': False, 'nullable': False}),
    'string': EditorialModel.fieldtypes.char.EmFieldType(**{'internal': 'automatic', 'max_length': 128, 'immutable': False, 'uniq': False, 'nullable': True}),
    'help_text': EditorialModel.fieldtypes.i18n.EmFieldType(**{'internal': False, 'uniq': False, 'nullable': False}),
    'fieldtype_options': EditorialModel.fieldtypes.dictionary.EmFieldType(**{'internal': False, 'uniq': False, 'nullable': False}),
    'date_update': EditorialModel.fieldtypes.datetime.EmFieldType(**{'now_on_update': True, 'nullable': False, 'uniq': False, 'internal': False}),
    'date_create': EditorialModel.fieldtypes.datetime.EmFieldType(**{'now_on_create': True, 'internal': False, 'uniq': False, 'nullable': False}),
    'rank': EditorialModel.fieldtypes.integer.EmFieldType(**{'internal': False, 'uniq': False, 'nullable': False})
}
Emcomponent.ml_fields_strings = {
   'superiors': MlString({"___": "superiors"}),
   'creation_date': MlString({"___": "creation_date", "eng": "Creation date", "fre": "Date de cr\u00e9ation"}),
   'name': MlString({"___": "name"}),
   'lodel_id': MlString({"___": "lodel_id", "eng": "lodel identifier", "fre": "identifiant lodel"}),
   'modification_date': MlString({"___": "modification_date", "eng": "Modification date", "fre": "Date de modification"}),
   'parent_class': MlString({"___": "parent_class"}),
   'fieldtype_options': MlString({"___": "fieldtype_options"}),
   'help_text': MlString({"___": "help_text"}),
   'rank': MlString({"___": "rank"}),
   'sort_column': MlString({"___": "sort_column"}),
   'fieldtype': MlString({"___": "fieldtype"}),
   'class_id': MlString({"___": "class_id", "eng": "class identifier", "fre": "identifiant de la classe"}),
   'selected_field': MlString({"___": "selected_field"}),
   'rel_field': MlString({"___": "rel_field"}),
   'string': MlString({"___": "string", "eng": "String representation", "fre": "Repr\u00e9sentation textuel"}),
   'type_id': MlString({"___": "type_id", "eng": "type identifier", "fre": "identifiant de la type"}),
   'classtype': MlString({"___": "classtype"}),
   'date_create': MlString({"___": "date_create"}),
   'nature': MlString({"___": "nature"}),
   'date_update': MlString({"___": "date_update"})
}
Emcomponent._linked_types = {
    'superiors': Emtype,
    'rel_field': Emfield,
    'classtype': Classtype,
    'parent_class': Emclass,
    'sort_column': Emfield,
    'selected_field': Emfield
}
Emcomponent._classtype = 'entity'

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
Emclass._fields = ['name', 'help_text', 'date_update', 'date_create', 'rank']
Emclass._superiors = {'parent': [Editorialmodel]}
Emclass._leclass = Emcomponent

#Initialisation of Emtype class attributes
Emtype._fields = ['name', 'help_text', 'date_update', 'date_create', 'rank']
Emtype._superiors = {'parent': [Emclass]}
Emtype._leclass = Emcomponent

#Initialisation of Emfield class attributes
Emfield._fields = ['name', 'help_text', 'date_update', 'date_create', 'rank', 'fieldtype', 'fieldtype_options']
Emfield._superiors = {'parent': [Emtype]}
Emfield._leclass = Emcomponent

## @brief Dict for getting LeClass and LeType child classes given an EM uid
LeObject._me_uid = {32: Emclass, 1: _Editorialmodel, 34: Emfield, 22: Emcomponent, 33: Emtype, 8: _Classtype, 31: Editorialmodel, 29: Classtype, 30: Hierarchyoptions, 15: _Hierarchy}
