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
    group = base_group,
    abstract=True
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
    data_handler = 'varchar',
    max_length = 5,
    uniq = True
)

em_lodel_site.new_field(
    'extensions',
    display_text = 'lodeSiteExtensions',
    help_text = 'Lodel site extensions',
    group = base_group,
    data_handler = 'list',
    back_reference = ('Plugin', 'plugin_name') 
)

em_lodel_site.new_field(
    'em_groups',
    display_text = 'lodelSiteEmGroups',
    help_text = 'Lodel site EM groups',
    group = base_group,
    data_handler = 'text',
)

pickle_file_path = 'examples/lodelsites_em.pickle'
xml_file_path = 'examples/lodelsites_em.xml'

em.save('xmlfile', filename=xml_file_path)
em.save('picklefile', filename=pickle_file_path)
