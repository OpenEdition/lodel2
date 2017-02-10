#-*- coding: utf-8 -*-
from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.leapi.leobject': ['LeObject'],
    'lodel.leapi.datahandlers.base_classes': ['DataField'],
    'lodel.plugin.hooks': ['LodelHook']})


class Abstract_Object(LeObject):
    _abstract = True
    _fields = None
    _uid = []
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class User(LeObject):
    _abstract = False
    _fields = None
    _uid = ['id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class Object(Abstract_Object):
    _abstract = True
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class Person(Object):
    _abstract = False
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class Entitie(Object):
    _abstract = True
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class Entry(Object):
    _abstract = True
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class Indexabs(Object):
    _abstract = True
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'dummy2'
    _child_classes = None


class Publication(Entitie):
    _abstract = False
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class Text(Entitie):
    _abstract = True
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class Text_Person(Entitie):
    _abstract = True
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class Indextheme(Indexabs):
    _abstract = False
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'dummy2'
    _child_classes = None


class Collection(Entitie):
    _abstract = False
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class Section(Text):
    _abstract = False
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


class Subsection(Section):
    _abstract = False
    _fields = None
    _uid = ['lodel_id']
    _ro_datasource = None
    _rw_datasource = None
    _datasource_name = 'default'
    _child_classes = None


Abstract_Object._set__fields({})
Abstract_Object._child_classes = (Person, Collection, Section, Entry, Publication, Object, Indextheme, Entitie, Text_Person, Subsection, Indexabs, Text,)
User._set__fields({
	'firstname': DataField.from_name('varchar')(**{ 'internal': False }), 
	'login': DataField.from_name('varchar')(**{ 'uniq': True, 'internal': False }), 
	'lastname': DataField.from_name('varchar')(**{ 'internal': False }), 
	'password': DataField.from_name('password')(**{ 'internal': False }), 
	'id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'classname': DataField.from_name('LeobjectSubclassIdentifier')(**{ 'internal': True })})
User._child_classes = tuple()
Object._set__fields({
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True })})
Object._child_classes = (Person, Collection, Section, Entry, Publication, Indextheme, Entitie, Text_Person, Subsection, Indexabs, Text,)
Person._set__fields({
	'firstname': DataField.from_name('varchar')(**{  }), 
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True }), 
	'lastname': DataField.from_name('varchar')(**{  }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'linked_texts': DataField.from_name('list')(**{ 'default': None, 'allowed_classes': [Text], 'nullable': True, 'back_reference': (Text, 'linked_persons') }), 
	'fullname': DataField.from_name('Concat')(**{ 'immutable': True, 'field_list': ['firstname', 'lastname'] }), 
	'alias': DataField.from_name('set')(**{ 'default': None, 'allowed_classes': [Person], 'nullable': True }), 
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'classname': DataField.from_name('LeobjectSubclassIdentifier')(**{ 'internal': True })})
Person._child_classes = tuple()
Entitie._set__fields({
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True })})
Entitie._child_classes = (Collection, Section, Publication, Text_Person, Subsection, Text,)
Entry._set__fields({
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True })})
Entry._child_classes = tuple()
Indexabs._set__fields({
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'value': DataField.from_name('varchar')(**{  }), 
	'name': DataField.from_name('varchar')(**{  }), 
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'theme': DataField.from_name('varchar')(**{  }), 
	'texts': DataField.from_name('list')(**{ 'allowed_classes': [Text], 'back_reference': (Text, 'indexes') })})
Indexabs._child_classes = (Indextheme,)
Publication._set__fields({
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True }), 
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'collection': DataField.from_name('link')(**{ 'default': None, 'allowed_classes': [Collection], 'nullable': True, 'back_reference': (Collection, 'publications') }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'classname': DataField.from_name('LeobjectSubclassIdentifier')(**{ 'internal': True })})
Publication._child_classes = tuple()
Text._set__fields({
	'linked_persons': DataField.from_name('list')(**{ 'default': None, 'allowed_classes': [Person], 'nullable': True, 'back_reference': (Person, 'linked_texts') }), 
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'subtitle': DataField.from_name('varchar')(**{ 'default': None, 'nullable': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'indexes': DataField.from_name('list')(**{ 'default': None, 'allowed_classes': [Indexabs], 'nullable': True, 'back_reference': (Indexabs, 'texts') }), 
	'title': DataField.from_name('varchar')(**{ 'nullable': True })})
Text._child_classes = (Subsection, Section,)
Text_Person._set__fields({
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True }), 
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'text': DataField.from_name('link')(**{ 'allowed_classes': [Text] }), 
	'person': DataField.from_name('link')(**{ 'allowed_classes': [Person] }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'role': DataField.from_name('varchar')(**{  })})
Text_Person._child_classes = tuple()
Indextheme._set__fields({
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'classname': DataField.from_name('LeobjectSubclassIdentifier')(**{ 'internal': True }), 
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'name': DataField.from_name('varchar')(**{  }), 
	'value': DataField.from_name('varchar')(**{  }), 
	'theme': DataField.from_name('varchar')(**{  }), 
	'texts': DataField.from_name('list')(**{ 'allowed_classes': [Text], 'back_reference': (Text, 'indexes') })})
Indextheme._child_classes = tuple()
Collection._set__fields({
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'publications': DataField.from_name('list')(**{ 'allowed_classes': [Publication], 'back_reference': (Publication, 'collection') }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True }), 
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'title': DataField.from_name('varchar')(**{  }), 
	'classname': DataField.from_name('LeobjectSubclassIdentifier')(**{ 'internal': True })})
Collection._child_classes = tuple()
Section._set__fields({
	'indexes': DataField.from_name('list')(**{ 'default': None, 'allowed_classes': [Indexabs], 'nullable': True, 'back_reference': (Indexabs, 'texts') }), 
	'subtitle': DataField.from_name('varchar')(**{ 'default': None, 'nullable': True }), 
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True }), 
	'childs': DataField.from_name('hierarch')(**{ 'default': None, 'allowed_classes': [Subsection], 'nullable': True, 'back_reference': (Subsection, 'parent') }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'linked_persons': DataField.from_name('list')(**{ 'default': None, 'allowed_classes': [Person], 'nullable': True, 'back_reference': (Person, 'linked_texts') }), 
	'classname': DataField.from_name('LeobjectSubclassIdentifier')(**{ 'internal': True }), 
	'title': DataField.from_name('varchar')(**{ 'nullable': True })})
Section._child_classes = (Subsection,)
Subsection._set__fields({
	'parent': DataField.from_name('link')(**{ 'default': None, 'allowed_classes': [Section], 'nullable': True, 'back_reference': (Section, 'childs') }), 
	'subtitle': DataField.from_name('varchar')(**{ 'default': None, 'nullable': True }), 
	'date_update': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_update': True }), 
	'date_create': DataField.from_name('datetime')(**{ 'internal': True, 'now_on_create': True }), 
	'childs': DataField.from_name('hierarch')(**{ 'default': None, 'allowed_classes': [Subsection], 'nullable': True, 'back_reference': (Subsection, 'parent') }), 
	'lodel_id': DataField.from_name('uniqid')(**{ 'internal': True }), 
	'linked_persons': DataField.from_name('list')(**{ 'default': None, 'allowed_classes': [Person], 'nullable': True, 'back_reference': (Person, 'linked_texts') }), 
	'help_text': DataField.from_name('text')(**{ 'internal': True }), 
	'indexes': DataField.from_name('list')(**{ 'default': None, 'allowed_classes': [Indexabs], 'nullable': True, 'back_reference': (Indexabs, 'texts') }), 
	'classname': DataField.from_name('LeobjectSubclassIdentifier')(**{ 'internal': True }), 
	'title': DataField.from_name('varchar')(**{ 'nullable': True })})
Subsection._child_classes = tuple()


#List of dynamically generated classes
dynclasses = [Abstract_Object, User, Object, Person, Entitie, Entry, Indexabs, Publication, Text, Text_Person, Indextheme, Collection, Section, Subsection]
#Dict of dynamically generated classes indexed by name
dynclasses_dict = {'Abstract_Object': Abstract_Object, 'User': User, 'Object': Object, 'Person': Person, 'Entitie': Entitie, 'Entry': Entry, 'Indexabs': Indexabs, 'Publication': Publication, 'Text': Text, 'Text_Person': Text_Person, 'Indextheme': Indextheme, 'Collection': Collection, 'Section': Section, 'Subsection': Subsection}

##@brief Return a dynamically generated class given it's name
#@param name str : The dynamic class name
#@return False or a child class of LeObject
def name2class(name):
    if name not in dynclasses_dict:
        return False
    return dynclasses_dict[name]


##@brief Return a dynamically generated class given it's name
#@note Case insensitive version of name2class
#@param name str
#@return False or a child class of LeObject
def lowername2class(name):
    name = name.lower()
    new_dict = {k.lower():v for k,v in dynclasses_dict.items()}
    if name not in new_dict:
        return False
    return new_dict[name]


##@brief Trigger dynclasses datasources initialisation
@LodelHook("lodel2_plugins_loaded")
def lodel2_dyncode_datasources_init(self, caller, payload):
    for cls in dynclasses:
        cls._init_datasources()
    LodelContext.expose_modules(globals(), {'lodel.plugin.hooks': ['LodelHook']})
    LodelHook.call_hook("lodel2_dyncode_loaded", __name__, dynclasses)


