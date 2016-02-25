#-*- coding: utf-8 -*-
from loader import *

import os, os.path, code

from EditorialModel.model import Model
from EditorialModel.backend.json_backend import EmBackendJson
from EditorialModel.classes import EmClass
from EditorialModel.types import EmType
from EditorialModel.fields import EmField
from EditorialModel.classtypes import *
from EditorialModel.fieldtypes.generic import GenericFieldType


emfile = 'em.json'

if not os.path.isfile(emfile):
    with open(emfile,'w+') as fd:
        fd.write('{}')

em = Model(EmBackendJson(emfile))


#GenericFieldType.from_name()

def ft(name):
    return GenericFieldType.from_name()


class_em = em.add_class('_EditorialModel', classtype = 'entity')
class_ctype = em.add_class('_ClassType', classtype='entity')
class_ctype_h = em.add_class('_Hierarchy', classtype='entity')
class_comp = em.add_class('EmComponent', classtype='entity')

class_emmod = em.add_class('_EmModification', classtype='entity')
#       class_ftype = em.add_class('_FieldType', classtype = 'entity')

#       type_ftype = em.add_type('FieldType', class_ftype)
type_ctype = em.add_type('ClassType', class_ctype)
type_ctype_h = em.add_type('HierarchyOptions', class_ctype_h)
type_em = em.add_type('EditorialModel', class_em)

type_class = em.add_type('EmClass', class_comp, superiors_list = {'parent': [type_em.uid]})
type_type = em.add_type('EmType', class_comp, superiors_list = {'parent':[type_class.uid]})
type_field = em.add_type('EmField', class_comp, superiors_list = {'parent':[type_type.uid]})


type_emmod = em.add_type('EmModification', class_emmod)
#        FieldType common fields
#       em.add_field('name', class_ftype, fieldtype = 'char', max_length = 56)
#       em.add_field('max_length', class_ftype, optional = True, fieldtype = 'integer')

# EditorialModel modification fields

# EditorialModel common fields
em.add_field('name', class_em, fieldtype = 'char', max_length = 56)
em.add_field('description', class_em, fieldtype = 'char', max_length = 4096)

# Hierarchy options common fields
em.add_field('attach', class_ctype_h, fieldtype = 'char', max_length = 10)
em.add_field('automatic', class_ctype_h, fieldtype = 'bool')
em.add_field('maxdepth', class_ctype_h, fieldtype = 'integer')
em.add_field('maxchildren', class_ctype_h, fieldtype = 'integer')

# ClassType common fields
em.add_field('name', class_ctype, fieldtype = 'char', max_length = 56)
field_hspec = em.add_field('hierarchy_specs', class_ctype, fieldtype = 'rel2type', rel_to_type_id = type_ctype_h)
em.add_field('nature', class_ctype, fieldtype = 'char', max_length = 10, rel_field_id = field_hspec.uid)

# EmComponent common fields
em.add_field('name', class_comp, fieldtype = 'char', max_length = 56)
# Part of default fields #em.add_field('string', class_comp, fieldtype = 'i18n')
em.add_field('help_text', class_comp, fieldtype = 'i18n', default={'en':'no help'})
em.add_field('date_update', class_comp, fieldtype = 'datetime', now_on_update = True, internal='automatic')
em.add_field('date_create', class_comp, fieldtype = 'datetime', now_on_create = True, internal='automatic')
#em.add_field('rank', class_comp, fieldtype = 'rank', internal='automatic')
# EmComponent optional fields
field_ctype = em.add_field('classtype', class_comp, optional = True, fieldtype = 'rel2type', rel_to_type_id = type_ctype.uid)
field_sortcol = em.add_field('sort_column', class_comp, optional = True, fieldtype = 'rel2type', rel_to_type_id = type_field.uid)

field_pclass = em.add_field('parent_class', class_comp, optional = True, fieldtype = 'rel2type', rel_to_type_id = type_class.uid)
field_selfield = em.add_field('selected_field', class_comp, optional = True, fieldtype = 'rel2type', rel_to_type_id = type_field.uid)
field_superior = em.add_field('superiors', class_comp, optional = True, fieldtype = 'rel2type', rel_to_type_id = type_type.uid)
field_nature = em.add_field('nature', class_comp, optional = True, fieldtype = 'char', max_length = 10, rel_field_id = field_superior.uid)

#       field_ftype = em.add_field('fieldtype', class_comp, optional = True, fieldtype = 'rel2type', rel_to_type_id = type_ftype)
field_ftype = em.add_field('fieldtype', class_comp, optional = True, fieldtype = 'char')
field_ftypeopt = em.add_field('fieldtype_options', class_comp, optional = True, fieldtype = 'dictionary')
field_relfield = em.add_field('rel_field', class_comp, optional = True, fieldtype = 'rel2type', rel_to_type_id = type_field)

# EmClass field selection
type_class.select_field(field_ctype)
type_class.select_field(field_sortcol)
# EmType field selection
type_type.select_field(field_sortcol)
type_type.select_field(field_pclass)
type_type.select_field(field_selfield)
type_type.select_field(field_superior)
type_type.select_field(field_nature)
# EmField field selection
type_field.select_field(field_ftype)
type_field.select_field(field_relfield)
type_field.select_field(field_ftypeopt)
em.save()

"""
print("Editorial model loaded in em variable : ")
for comptype in [ 'EmClass', 'EmType', 'EmField' ]:
    print("\t* %s :" % comptype)
    complist = em.components(comptype)
    if len(complist) == 0:
        print("\t\tEMPTY")
    for comp in complist:
       print("\t\t- %s" % comp.name)


code.interact(local=locals())
"""
