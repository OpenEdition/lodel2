#-*- coding: utf-8 -*-

from lodel.editorial_model.components import *
from lodel.editorial_model.exceptions import *
from lodel.editorial_model.model import EditorialModel

em = EditorialModel('testem', 'Test editorial model')

base_group = em.new_group(  'base_group',
                            display_name = 'Base group',
                            help_text = 'Base group that implements base EM features (like classtype)'
)

####################
#   Lodel Object   #
####################
em_object = em.new_class(   'object',
                            display_name = 'Object',
                            help_text = 'Main class for all Em objects',
                            group = base_group,
                            abstract = True,
)
em_object.new_field(    'lodel_id',
                        display_name = 'Lodel identifier',
                        help_text = 'Uniq ID that identify every lodel object',
                        group = base_group,
                        data_handler = 'uniqid',
                        internal = True,
)
em_object.new_field(    'help_text',
                        display_name = 'Help',
                        help_text = 'A short text that describe the object',
                        group = base_group,
                        internal = True,
                        data_handler = 'text',
)

em_object.new_field(    'date_create',
                        display_name = 'Creation date',
                        group = base_group,
                        data_handler = 'datetime',
                        now_on_create = True,
)
em_object.new_field(    'date_update',
                        display_name = 'Last update',
                        group = base_group,
                        data_handler = 'datetime',
                        now_on_update = True,
)
em_object.new_field(    'classname',
                        display_name = 'Class name',
                        group = base_group,
                        data_handler = 'varchar',
                        immutable = True
)

########################
# Lodel old classtypes #
########################
entitie = em.new_class( 'entitie',
                        display_name = 'entitie',
                        help_text = 'Replace old entity classtype',
                        abstract = True,
                        group = base_group,
                        parents = em_object,
)

person = em.new_class(  'person',
                        display_name = 'Person',
                        help_text = 'Replace old person classtype',
                        abstract = True,
                        group = base_group,
                        parents = em_object,
)

person.new_field(   'firstname',
                    display_name = {
                        'eng': 'Firstname',
                        'fre': 'Prénom',
                    },
                    data_handler = 'varchar',
)
person.new_field(   'lastname',
                    display_name = {
                        'eng': 'Lastname',
                        'fre': 'Nom de famille',
                    },
                    data_handler = 'varchar',
)
person.new_field(   'fullname',
                    display_name = {
                        'eng': 'Fullname',
                        'fre': 'Nom complet',
                    },
                    group = base_group,
                    data_handler = 'varchar', # <-- should be concat type
                    internal = True,
                    immutable = True,
)
person.new_field(   'alias',
                    display_name = 'alias',
                    help_text = {
                        'eng': 'Link to other person class instance that represent the same person',
                        'fre': 'Lien vers un ensemble d\'instances de la classe personne représentant le même individu',
                    },
                    data_handler = 'set',
                    allowed_classes = [person],
)


entry = em.new_class(   'entry',
                        display_name = 'Entry',
                        help_text = 'Replace olf entry classtype',
                        abstract = True,
                        group = base_group,
                        parents = em_object,
)

#####################
# Editorial classes #
#####################

editorial_group = em.new_group( 'editorial_abstract',
                                display_name = 'Editorial base',
                                help_text = {
                                    'eng': 'Contains abstract class to handler editorial contents',
                                    'fre': 'Contient les classes abstraites permetant la gestion de contenu éditorial'
                                },
                                depends = (base_group,)
)

# Classe texte
text = em.new_class(   'text',
                        display_name = 'Text',
                        help_text = 'Abstract class that represent texts',
                        group = editorial_group,
                        abstract = True,
                        parents = entitie,
)

text.new_field(    'title',
                    display_name = {'eng': 'Title', 'fre': 'Titre'},
                    group = editorial_group,
                    data_handler = 'varchar',
)
text.new_field(    'subtitle',
                    display_name = {
                        'eng': 'Subtitle',
                        'fre': 'Sous-titre',
                    },
                    group = editorial_group,
                    data_handler = 'varchar',
)

# Classe collection
collection = em.new_class(  'collection',
                            display_name = 'Collection',
                            group = editorial_group,
                            abstract = True,
                            parents = entitie,
)
collection.new_field(   'title',
                        display_name = 'Title',
                        group = editorial_group,
                        abstract = True,
                        data_handler = 'varchar'
)

#####################
# Persons & authors #
#####################

editorial_person_group = em.new_group(  'editorial_person',
                                        display_name = 'Editorial person',
                                        help_text = {
                                            'eng': 'Introduce the concept of editorial person (authors, translator etc)',
                                            'fre': 'Contient les classes servant à la gestion des personnes editorials (auteurs, traducteur...)',
                                        },
                                        depends = (editorial_group,)
)
text_person = em.new_class( 'text_person',
                            display_name = {
                                'eng': 'TextPerson',
                                'fre': 'TextePersonne',
                            },
                            help_text = {
                                'eng': 'Represent a link between someone and a text',
                                'fre': 'Représente un lien entre une personne et un texte',
                            },
                            group = editorial_person_group,
                            abstract = True,
                            parents = entitie,
)
bref_textperson_text = text_person.new_field(  'text',
                                                display_name = {
                                                    'eng': 'Linked text',
                                                    'fre': 'Texte lié',
                                                },
                                                data_handler = 'link',
                                                allowed_classes = [text],
                                                group = editorial_person_group
)
bref_textperson_person = text_person.new_field( 'person',
                                                display_name = {
                                                    'eng': 'Linked person',
                                                    'fre': 'Personne liée',
                                                },
                                                data_handler = 'link',
                                                allowed_classes = [person],
                                                group = editorial_person_group,
)
text_person.new_field(  'role',
                        display_name = {
                            'eng': 'Person role',
                            'fre': 'Role de la personne',
                        },
                        data_handler = 'varchar',
                        group = editorial_person_group
)

# simple example of linked text / person
person.new_field(   'linked_texts',
                    display_name = {
                        'eng': 'Linked texts',
                        'fre': 'Textes liés',
                    },
                    data_handler = 'list',
                    back_reference = ('Text', 'lodel_id'),
                    group = editorial_person_group,
)

text.new_field( 'linked_persons',
                display_name = {
                    'eng': 'Linked persons',
                    'fre': 'Personnes liées',
                },
                data_handler = 'list',
                back_reference = ('Person', 'lodel_id'),
                group = editorial_person_group,
)

print(person.parents_recc)
em.save('picklefile', filename = 'examples/em_test.pickle')
