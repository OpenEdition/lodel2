import imp
import importlib
import sys
import types
import collections

import django
from django.db import models
from django.contrib import admin


from EditorialModel.classes import EmClass
from EditorialModel.types import EmType
from EditorialModel.fields import EmField
from EditorialModel.fieldtypes import EmFieldType

##
# @source https://code.djangoproject.com/wiki/DynamicModels
#
def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta':Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)
    return model


module = 'poc'

#Definition degueu du ME de test (degueu car orderedDict)
em_example = collections.OrderedDict()

em_example['publication'] = {
        'fields': {
            'title': {
                'fieldtype': 'CharField',
                'opts': {'max_length':32},
            },
            'doi': {
                'fieldtype': 'CharField',
                'opts': {'max_length':32, 'default':None},
                'optionnal': True,
            },
        },
        'types': collections.OrderedDict([
            ('collection', {
                'sups': ['collection'],
                'opt_field': (),
            }),
            ('numero', {
                'sups': ['collection'],
                'opt_field': ('doi'),
            }),
        ]),
    }

em_example['texte'] = {
        'fields': {
            'title': {
                'fieldtype': 'CharField',
                'opts': {'max_length':32},
            },
            'content': {
                'fieldtype': 'TextField',
                'opts': {},
            },
            'doi': {
                'fieldtype': 'CharField',
                'opts': {'max_length':32},
                'optionnal': True,
            },
        },
        'types': {
            'article': {
                'sups': ['numero'],
                'opt_field': ('doi'),
            },
            'preface': {
                'sups': ['numero'],
                'opt_field': (),
            },
        },
    }

em_example['contributor'] = {
        'fields': {
            'name':{
                'fieldtype': 'CharField',
                'opts': {'max_length':32},
            },
            'linked_text': {
                'fieldtype': 'ManyToManyField',
                'opts': {'to': 'texte'},
            },
        },
        'types': {
            'author': { 'sups': [] },
            'director': { 'sups': [] },
        },
    }

#
# Fin ME
#

# LeObject model
leobj_attr = {
    'lodel_id': models.IntegerField(primary_key=True),
}

leobject = create_model('leobject', leobj_attr, module)

# Create all the models from the EM datas
def em_to_models(em):
    result = {}
    for cname, em_class in em.items():
        cls_attr = { 'lodel_id': models.ForeignKey(leobject, primary_key=True) }
        result[cname] = create_model(cname, cls_attr, module)
            
        #Creating type table
        for tname, em_type in em_class['types'].items():
            print('type : ', tname)

            type_attr = { 'lodel_id': models.ForeignKey(leobject, primary_key=True)}

            if 'sups' in em_type:
                for superior in em_type['sups']:
                    type_attr[superior+'_superior'] = models.ForeignKey( 'self' if superior == tname else result[superior])

            for fname, em_field in em_class['fields'].items():
                if not 'optionnal' in em_field or not em_field['optionnal'] or ('opt_field' in em_type and fname in em_type['opt_field']):
                    field = getattr(models, em_field['fieldtype'])
                    if 'opts' in em_field and len(em_field['opts']):
                        opts = em_field['opts']
                    else:
                        opts = {}
                    type_attr[fname] = field(**opts)
            print("Debug : adding ", tname)
            result[tname] = create_model(tname, type_attr, module)
    return result

models = em_to_models(em_example)
