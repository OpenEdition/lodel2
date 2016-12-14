#!/usr/bin/python3
#-*- coding: utf-8 -*-

from lodel.context import LodelContext
LodelContext.init()

from lodel.settings.settings import Settings as settings
settings('globconf.d')
from lodel.settings import Settings

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
em_abstract = em.new_class( 'abstract_object',
    display_name = 'Abstract lodel object',
    help_text = 'For testing purpose',
    group = base_group,
    abstract = True)

em_object = em.new_class(   'object',
                            display_name = 'Object',
                            help_text = 'Main class for all Em objects',
                            group = base_group,
                            abstract = True,
                            parents = em_abstract,
)
em_object.new_field(    'lodel_id',
                        display_name = 'Lodel identifier',
                        help_text = 'Uniq ID that identify every lodel object',
                        group = base_group,
                        data_handler = 'uniqid',
                        internal = True,
)
em_object.new_field(    'date_create',
                        display_name = 'Creation date',
                        group = base_group,
                        data_handler = 'datetime',
                        now_on_create = True,
                        internal = True,
)
em_object.new_field(    'date_update',
                        display_name = 'Last update',
                        group = base_group,
                        data_handler = 'datetime',
                        now_on_update = True,
                        internal = True,
)
entitie = em.new_class( 'entitie',
                        display_name = 'entitie',
                        help_text = 'Replace old entity classtype',
                        abstract = True,
                        group = base_group,
                        parents = em_object,
)
########################
# Base group
########################

person = em.new_class(  'person',
                        display_name = 'Person',
                        help_text = 'Person type',
                        abstract = False,
                        group = base_group,
                        parents = em_object,
)

person.new_field(   'firstname',
                    display_name = {
                        'eng': 'Firstname',
                        'fre': 'Prénom',
                    },
                    data_handler = 'varchar',
                    group = base_group,
)
person.new_field(   'lastname',
                    display_name = {
                        'eng': 'Lastname',
                        'fre': 'Nom de famille',
                    },
                    data_handler = 'varchar',
                    group = base_group,
)

# person.new_field(   'role',
#                     display_name = {
#                         'eng': 'Role',
#                         'fre': 'Rôle',
#                     },
#                     data_handler = 'varchar',
#                     group = base_group,
# )

entry = em.new_class(   'entry',
                        display_name = 'Entry',
                        help_text = 'Entry type',
                        abstract = False,
                        group = base_group,
                        parents = em_object,
)
entry.new_field(    'name',
                    display_name = {
                        'eng': 'Name',
                        'fre': 'Nom',
                    },
                    data_handler = 'varchar',
                    group = base_group,
)
entry.new_field(    'description',
                    display_name = {
                        'eng': 'Description',
                        'fre': 'Description',
                    },
                    data_handler = 'text',
                    group = base_group,
)

entry.new_field(    'role',
                    display_name = {
                        'eng': 'Role',
                        'fre': 'Rôle',
                    },
                    data_handler = 'varchar',
                    group = base_group,
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

################################### Texts ##########################################################
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
                    data_handler = 'text',
                    nullable = True,)
text.new_field(    'subtitle',
                    display_name = {
                        'eng': 'Subtitle',
                        'fre': 'Sous-titre',
                    },
                    group = editorial_group,
                    data_handler = 'text',
                    nullable = True,
                    default = None)
text.new_field(    'language',
                    display_name = {
                        'eng': 'Language',
                        'fre': 'Langue',
                    },
                    group = editorial_group,
                    data_handler = 'varchar',
                    nullable = True,
                    default = None)
text.new_field(    'text',
                    display_name = {
                        'eng': 'Text',
                        'fre': 'Texte',
                    },
                    group = editorial_group,
                    data_handler = 'text',
                    nullable = True,
                    default = None)
text.new_field(    'pub_date',
                    display_name = {
                        'eng': 'Publication date',
                        'fre': 'Date de publication',
                    },
                    group = editorial_group,
                    data_handler = 'datetime',
                    nullable = True,
                    default = None)
text.new_field(    'footnotes',
                    display_name = {
                        'eng': 'Footnotes',
                        'fre': 'Notes de bas de page',
                    },
                    group = editorial_group,
                    data_handler = 'text',
                    nullable = True,
                    default = None)
text.new_field(    'linked_entries',
                    display_name = {
                        'eng': 'Related entries',
                        'fre': 'Indices liés',
                    },
                    group = editorial_group,
                    data_handler = 'list',
                    nullable = True,
                    allowed_classes = [entry],
                    back_reference = ('entry', 'linked_texts'),
                    default = None
)
entry.new_field(    'linked_texts',
                    display_name = {
                        'eng': 'Related text',
                        'fre': 'Texte lié ',
                    },
                    data_handler = 'list',
                    nullable = True,
                    allowed_classes = [text],
                    group = editorial_group,
                    back_reference = ('text', 'linked_entries'),
                    default = None
)
# Classe article
article = em.new_class( 'article',
                        display_name = 'Article',
                        group = editorial_group,
                        abstract = False,
                        parents = text)
article.new_field(  'abstract',
                    display_name = {
                        'eng': 'Abstract',
                        'fre': 'Résumé',
                    },
                    group = editorial_group,
                    data_handler = 'text'
)
article.new_field(  'appendix',
                    display_name = {
                        'eng': 'Appendix',
                        'fre': 'Appendice',
                    },
                    group = editorial_group,
                    data_handler = 'text'
)
article.new_field(  'bibliography',
                    display_name = {
                        'eng': 'Bibliography',
                        'fre': 'Bibliographie',
                    },
                    group = editorial_group,
                    data_handler = 'text'
)
article.new_field(  'author_note',
                    display_name = {
                        'eng': 'Author note',
                        'fre': "Note de l'auteur",
                    },
                    group = editorial_group,
                    data_handler = 'text'
)
# Classe Review 
review = em.new_class( 'review',
                        display_name = 'Review',
                        group = editorial_group,
                        abstract = False,
                        parents = text)
review.new_field(   'reference',
                    display_name = {
                        'eng': 'Reference',
                        'fre': "Référence",
                    },
                    group = editorial_group,
                    data_handler = 'text'
)

###################################### Containers ###########################################
# Classe container
container = em.new_class(  'container',
                            display_name = 'Container',
                            group = editorial_group,
                            abstract = True,
                            parents = entitie)
container.new_field(   'title',
                        display_name = 'Title',
                        group = editorial_group,
                        data_handler = 'text'
)
container.new_field(   'subtitle',
                        display_name = 'Subtitle',
                        group = editorial_group,
                        data_handler = 'text'
)
container.new_field(   'language',
                        display_name = {
                            'eng' : 'Language',
                            'fre' : 'Langue',
                        },
                        group = editorial_group,
                        data_handler = 'varchar'
)
container.new_field(    'linked_directors',
                    display_name = {
                        'eng': 'Directors',
                        'fre': 'Directeurs',
                    },
                    group = editorial_group,
                    data_handler = 'list',
                    nullable = True,
                    allowed_classes = [person],
                    back_reference = ('person', 'linked_containers'),
                    default = None
)
person.new_field(   'linked_containers',
                    display_name = {
                        'eng': 'Director of ',
                        'fre': 'Directeur de ',
                    },
                    group = editorial_group,
                    data_handler = 'list',
                    nullable = True,
                    allowed_classes = [container],
                    back_reference = ('container', 'linked_directors'),
                    default = None
)
container.new_field(    'description',
                    display_name = {
                        'eng': 'Description',
                        'fre': 'Description',
                    },
                    data_handler = 'text',
                    group = editorial_group,
)
container.new_field(    'publisher_note',
                    display_name = {
                        'eng': 'Publisher note',
                        'fre': "Note de l'éditeur",
                    },
                    data_handler = 'text',
                    group = editorial_group,
)

# Classe collection
collection = em.new_class(  'collection',
                            display_name = 'Collection',
                            group = editorial_group,
                            abstract = False,
                            parents = container)
collection.new_field(    'issn',
                    display_name = {
                        'eng': 'ISSN',
                        'fre': "ISSN",
                    },
                    data_handler = 'varchar',
                    group = editorial_group,
)
# Classe Publication : Pour gérer les back_references vers issue ou part
publication = em.new_class(  'publication',
                            display_name = 'Publication',
                            group = editorial_group,
                            abstract = True,
                            parents = container)
publication.new_field(  'linked_texts',
                        display_name = {
                            'eng': 'Text',
                            'fre': 'Texte',
                        },
                      data_handler = 'list',
                    nullable = True,
                    allowed_classes = [text],
                    group = editorial_group,
                    back_reference = ('text', 'linked_container'),
                    default = None
)
text.new_field(    'linked_container',
                    display_name = {
                        'eng': 'Container',
                        'fre': 'Conteneur',
                    },
                    data_handler = 'link',
                    nullable = True,
                    allowed_classes = [publication],
                    group = editorial_group,
                    back_reference = ('publication', 'linked_texts'),
                    default = None
)
# Classe Issue
issue = em.new_class( 'issue',
                        display_name = 'Issue',
                        group = editorial_group,
                        abstract = False,
                        parents = publication)
issue.new_field(    'isbn',
                  display_name = 'ISBN',
                  data_handler = 'varchar',
                  group = editorial_group,
)
issue.new_field(    'print_isbn',
                  display_name = {
                    'eng': 'Printed ISBN',
                    'fre': "ISBN imprimé",
                  },
                  data_handler = 'varchar',
                  group = editorial_group,
)
issue.new_field(    'number',
                    display_name = {
                        'eng': 'Number',
                        'fre': 'Numéro',
                    },
                  data_handler = 'varchar',
                  group = editorial_group,
)
issue.new_field(    'cover',
                    display_name = {
                        'eng': 'Cover',
                        'fre': 'Couverture',
                    },
                  data_handler = 'varchar',
                  group = editorial_group,
)
issue.new_field(    'print_pub_date',
                    display_name = {
                        'eng': 'Print date',
                        'fre': "Date d'impression",
                    },
                  data_handler = 'datetime',
                  group = editorial_group,
)     
issue.new_field(    'e_pub_date',
                    display_name = {
                        'eng': 'Electronic publication date',
                        'fre': 'Date de publication électronique',
                    },
                  data_handler = 'datetime',
                  group = editorial_group,
)  
issue.new_field(    'abstract',
                    display_name = {
                        'eng': 'Abstract',
                        'fre': 'Résumé',
                    },
                  data_handler = 'text',
                  group = editorial_group,
) 
issue.new_field(    'collection',
                    display_name = {
                        'eng': 'Collection',
                        'fre': 'Collection',
                    },
                    data_handler = 'link',
                    nullable = True,
                    allowed_classes = [collection],
                    group = editorial_group,
                    back_reference = ('collection', 'linked_issues'),
                    default = None
)
collection.new_field(   'linked_issues',
                        display_name = {
                        'eng': 'Linked issues',
                        'fre': 'Numéros',
                    },
                    data_handler = 'hierarch',
                    back_reference = ('Issue', 'collection'),
                    group = editorial_group,
                    allowed_classes = [issue],
                    default = None,
                    nullable = True)
# Classe Part
part = em.new_class(  'part',
                            display_name = 'Part',
                            group = editorial_group,
                            abstract = False,
                            parents = publication,)
part.new_field(     'publication',
                    display_name = {
                        'eng': 'Publication',
                        'fre': 'Publication',
                    },
                    data_handler = 'link',
                    nullable = True,
                    allowed_classes = [publication],
                    group = editorial_group,
                    back_reference = ('publication', 'linked_parts'),
                    default = None
)
publication.new_field(  'linked_parts',
                        display_name = {
                            'eng': 'Parts',
                            'fre': 'Parties',
                        },
                      data_handler = 'hierarch',
                    nullable = True,
                    allowed_classes = [part],
                    group = editorial_group,
                    back_reference = ('part', 'publication'),
                    default = None
)

#####################
# Persons & authors #
#####################

editorial_person_group = em.new_group(  'editorial_person',
                                        display_name = 'Editorial person',
                                        help_text = {
                                            'eng': 'Introduce the concept of editorial person (author, translator, director)',
                                            'fre': 'Contient les classes servant à la gestion des personnes éditoriales (auteur, traducteur, directeur...)',
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
                    back_reference = ('Text', 'linked_persons'),
                    group = editorial_person_group,
                    allowed_classes = [text],
                    default = None,
                    nullable = True)

text.new_field( 'linked_persons',
                display_name = {
                    'eng': 'Linked persons',
                    'fre': 'Personnes liées',
                },
                data_handler = 'list',
                back_reference = ('Person', 'linked_texts'),
                group = editorial_person_group,
                allowed_classes = [person],
                default = None,
                nullable = True)

#####################
# Index classes     # <--- Note :   using a different datasource for testing
#####################               purpose

index_group = em.new_group( 'index_group',
                            display_name = 'Indexes',
                            help_text = {
                                'eng': 'EM class that represents indexes'},
                            depends = (editorial_group,))

index_abstract = em.new_class(
    'indexAbs',
    display_name = {'eng': 'Abstract Index'},
    help_text = {'eng': 'Abstract class common to each Index classes'},
    abstract = True,
    group = index_group,
    datasources = 'dummy2',
    parents = em_object)

index_name = index_abstract.new_field(
    'name',
    display_name = {
        'eng': 'name',
        'fre': 'nom'},
    data_handler = 'text',
    group = index_group)

index_value = index_abstract.new_field(
    'value',
    display_name = {
        'eng': 'value',
        'fre': 'valeur'},
    data_handler = 'varchar',
    group = index_group)

text.new_field( 'indexes',
    display_name = {
        'eng': 'Indexes',
        'fre': 'Indexes'},
    data_handler = 'list',
    back_reference = ('Indexabs', 'texts'),
    allowed_classes = [index_abstract],
    default = None,
    nullable = True,
    group = index_group)

index_abstract.new_field( 'texts',
    display_name = {
        'eng': 'Text referenced by this index',
        'fre': 'Texte contenant cette index'},
    data_handler = 'list',
    back_reference = ('Text', 'indexes'),
    allowed_classes = [text],
    group = index_group)

index_theme = em.new_class(
    'indexTheme',
    display_name = {
        'eng': 'Thematic index',
        'fre': 'Index thématique'},
    group = index_group,
    datasources = 'dummy2',
    parents = index_abstract)

index_theme_theme = index_abstract.new_field(
    'theme',
    display_name = {
        'eng': 'theme'},
    data_handler = 'varchar',
    group = index_group)

#############
#   USERS   #
#############

user_group = em.new_group(
    'users', display_name = 'Lodel users',
    help_text = 'Group that handle users en perm')

user = em.new_class(
    'user', display_name = 'Lodel user', help_text = 'Represent a lodel user',
    group = user_group, abstract = False)

user.new_field(
    'id', display_name = 'user identifier', help_text = 'Uniq ID',
    group = user_group, data_handler = 'uniqid', internal = True)

user.new_field(
    'firstname', display_name = 'Firstname',
    group = user_group, data_handler = 'varchar', internal = False)

user.new_field(
    'lastname', display_name = 'Lastname',
    group = user_group, data_handler = 'varchar', internal = False)

user.new_field(
    'login', display_name = 'user login', help_text = 'login',
    group = user_group, data_handler = 'varchar', uniq = True, internal = False)

user.new_field(
    'password', display_name = 'Password',
    group = user_group, data_handler = 'password', internal = False)


#em.save('xmlfile', filename = 'examples/em_test.xml')
pickle_file = 'examples/em_test.pickle'
em.save('picklefile', filename = pickle_file)
print("Output written in %s" % pickle_file)
