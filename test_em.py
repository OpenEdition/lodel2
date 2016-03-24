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
                        data_handler = 'integer',
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
texte = em.new_class(   'text',
                        display_name = 'Text',
                        help_text = 'Abstract class that represent texts',
                        group = editorial_group,
                        abstract = True,
)

texte.new_field(    'title',
                    display_name = {'eng': 'Title', 'fre': 'Titre'},
                    group = editorial_group,
                    data_handler = 'varchar',
)
texte.new_field(    'subtitle',
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
)
collection.new_field(   'title',
                        display_name = 'Title',
                        group = editorial_group,
                        abstract = True,
                        data_handler = 'varchar'
)
