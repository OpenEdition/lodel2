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

em = EditorialModel('LodelSites', 'LodelSites editorial model')

base_group = em.new_group(
    'base_group',
    display_name = 'Base group',
    help_text = 'Base group that implements base EM features (like classtype)'
)

em_lodel_site = em.new_class(
    'LodelSite',
    group = base_group
)

em_lodel_site.new_field(
    'name',
    display_name = 'lodelSiteName',
    help_text = 'Lodel site full name',
    group = base_group,
    data_handler = 'varchar'
)

em_lodel_site.new_field(
    'shortname',
    display_text = 'lodelSiteShortName',
    help_text = 'Lodel site short string identifier',
    group = base_group,
    data_handler = 'regex',
    max_length = 5,
    regex = '^[0-9a-z_-]+$',
    primary_key = True
)

em_lodel_site.new_field(
    'extensions',
    display_text = 'lodeSiteExtensions',
    help_text = 'Lodel site extensions',
    group = base_group,
    data_handler = 'varcharlist',
    delimiter = ' '
)

em_lodel_site.new_field(
    'em_groups',
    display_text = 'lodelSiteEmGroups',
    help_text = 'Lodel site EM groups',
    group = base_group,
    data_handler = 'text',
)




user_group = em.new_group(
    'users',
    display_name = 'Lodel users',
    help_text = 'Group that handle users en perm'
)


user = em.new_class(
    'User',
    group = user_group
)

user.new_field(
    'login',
    display_name = 'User login',
    help_text = 'login',
    group = user_group,
    data_handler = 'varchar',
    primary_key = True
)

user.new_field(
    'password',
    display_name = 'Password',
    help_text = 'User password',
    group = user_group,
    data_handler = 'password',
)


pickle_file_path = 'examples/lodelsites_em.pickle'
xml_file_path = 'examples/lodelsites_em.xml'

em.save('xmlfile', filename=xml_file_path)
em.save('picklefile', filename=pickle_file_path)
