# -*- coding: utf-8 -*-

#from django.conf import settings
#settings.configure(DEBUG=True)
import os
import sys

import django
from django.db import models
from django.db.models.loading import cache as django_cache
from django.core.exceptions import ValidationError

from EditorialModel.exceptions import *

#django.conf.settings.configure(DEBUG=True)


## @brief Create a django model
# @param name str : The django model name
# @param fields dict : A dict that contains fields name and type ( str => DjangoField )
# @param app_label str : The name of the applications that will have those models
# @param module str : The module name this model will belong to
# @param options dict : Dict of options (name => value)
# @param admin_opts dict : Dict of options for admin part of this model
# @param parent_class str : Parent class name
# @return A dynamically created django model
# @source https://code.djangoproject.com/wiki/DynamicModels
#
def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None, parent_class=None):
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
    if parent_class is None:
        parent_class = models.Model
    model = type(name, (parent_class,), attrs)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)
    return model


## @package EditorialModel.migrationhandler.django
# @brief A migration handler for django ORM
#
# Create django models according to the editorial model

class DjangoMigrationHandler(object):

    ##
    # @param app_name str : The django application name for models generation
    # @param debug bool : Set to True to be in debug mode
    # @warning DONT use self.models it does not contains all the models (none of the through models for rel2type)
    def __init__(self, app_name, debug=False, dryrun=False):
        self.models = {}
        self.debug = debug
        self.app_name = app_name
        self.dryrun = dryrun

    ## @brief Record a change in the EditorialModel and indicate wether or not it is possible to make it
    # @note The states ( initial_state and new_state ) contains only fields that changes
    #
    # @note Migration is not applied by this method. This method only checks if the new em is valid
    #
    # @param em model : The EditorialModel.model object to provide the global context
    # @param uid int : The uid of the change EmComponent
    # @param initial_state dict | None : dict with field name as key and field value as value. Representing the original state. None mean creation of a new component.
    # @param new_state dict | None : dict with field name as key and field value as value. Representing the new state. None mean component deletion
    # @throw EditorialModel.exceptions.MigrationHandlerChangeError if the change was refused
    # @todo Some tests about strating django in this method
    # @todo Rename in something like "validate_change"
    #
    # @warning broken because of : https://code.djangoproject.com/ticket/24735 you have to patch django/core/management/commands/makemigrations.py w/django/core/management/commands/makemigrations.py
    def register_change(self, em, uid, initial_state, new_state):
        
        #Starting django
        os.environ['LODEL_MIGRATION_HANDLER_TESTS'] = 'YES'
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")
        django.setup()
        from django.contrib import admin
        from django.core.management import call_command as django_cmd

        if self.debug:
            self.dump_migration(uid, initial_state, new_state)

        #Generation django models
        self.em_to_models(em)
        try:
            #Calling makemigrations to see if the migration is valid
            #django_cmd('makemigrations', self.app_name, dry_run=True, interactive=False, merge=True)
            django_cmd('makemigrations', self.app_name, dry_run=True, interactive=False)
        except django.core.management.base.CommandError as e:
            raise MigrationHandlerChangeError(str(e))
    
        return True

    ## @brief Print a debug message representing a migration
    def dump_migration(self, uid, initial_state, new_state):
        if self.debug:
            print("\n##############")
            print("DummyMigrationHandler debug. Changes for component with uid %d :" % uid)
            if initial_state is None:
                print("Component creation (uid = %d): \n\t" % uid, new_state)
            elif new_state is None:
                print("Component deletion (uid = %d): \n\t" % uid, initial_state)
            else:
                field_list = set(initial_state.keys()).union(set(new_state.keys()))
                for field_name in field_list:
                    str_chg = "\t%s " % field_name
                    if field_name in initial_state:
                        str_chg += "'" + str(initial_state[field_name]) + "'"
                    else:
                        str_chg += " creating "
                    str_chg += " => "
                    if field_name in new_state:
                        str_chg += "'" + str(new_state[field_name]) + "'"
                    else:
                        str_chg += " deletion "
                    print(str_chg)
            print("##############\n")
        pass
    
    ## @brief Register a new model state and update the data representation given the new state
    # @param em model : The EditorialModel to migrate
    # @param state_hash str : Note usefull (for the moment ?)
    # @todo Rename this method in something like "model_migrate"
    def register_model_state(self, em, state_hash):
        if self.dryrun:
            return
        if self.debug:
            print("Applying editorial model change")

        #Starting django
        os.environ['LODEL_MIGRATION_HANDLER_TESTS'] = 'YES'
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")
        django.setup()
        from django.contrib import admin
        from django.core.management import call_command as django_cmd

        #Generation django models
        self.em_to_models(em)
        try:
            #Calling makemigrations
            django_cmd('makemigrations', self.app_name, interactive=False)
        except django.core.management.base.CommandError as e:
            raise MigrationHandlerChangeError(str(e))

        try:
            #Calling migrate to update the database schema
            django_cmd('migrate', self.app_name, interactive=False, noinput=True)
        except django.core.management.base.CommandError as e:
            raise MigrationHandlerChangeError("Unable to migrate to new model state : %s"%e)

        pass

    ## @brief Return the models save method
    #
    # The save function of our class and type models is used to set unconditionnaly the
    # classtype, class_name and type_name models property
    # 
    # @param classname str: The classname used to call the super().save
    # @param level str: Wich type of model are we doing. Possible values are 'class' and 'type'
    # @param datas list : List of property => value to set in the save function
    # @return The wanted save function
    def get_save_fun(self, classname, level, datas):
        
        if level == 'class':
            def save(self, *args, **kwargs):
                self.classtype = datas['classtype']
                self.class_name = datas['class_name']
                super(classname, self).save(*args, **kwargs)
        elif level == 'type':
            def save(self, *args, **kwargs):
                self.type_name = datas['type_name']
                super(classname, self).save(*args, **kwargs)

        return save
    
    ## @brief Create django models from an EditorialModel.model object
    # @param edMod EditorialModel.model.Model : The editorial model instance
    # @return a dict with all the models
    # @todo Handle fieldgroups
    # @todo write and use a function to forge models name from EmClasses and EmTypes names
    # @note There is a problem with the related_name for superiors fk : The related name cannot be subordinates, it has to be the subordinates em_type name
    def em_to_models(self, edMod):
        
        module_name = self.app_name+'models'

        #Purging django models cache
        if self.app_name in django_cache.all_models:
            for modname in django_cache.all_models[self.app_name]:
                del(django_cache.all_models[self.app_name][modname])
            #del(django_cache.all_models[self.app_name])

        #This cache at instance level seems to be useless...
        del(self.models)
        self.models = {}

        app_name = self.app_name
        #Creating the document model
        document_attrs = {
            'lodel_id' : models.AutoField(primary_key=True),
            'classtype': models.CharField(max_length=16, editable=False),
            'class_name': models.CharField(max_length=16, editable=False),
            'type_name': models.CharField(max_length=16, editable=False),
            'string' : models.CharField(max_length=255),
            'date_update': models.DateTimeField(auto_now=True, auto_now_add=True),
            'date_create': models.DateTimeField(auto_now_add=True),
            'rank' : models.IntegerField(),
            'help_text': models.CharField(max_length=255),
        }

        #Creating the base model document
        document_model = create_model('document', document_attrs, self.app_name, module_name)

        django_models = {'doc' : document_model, 'classes':{}, 'types':{} }

        classes = edMod.classes()

        #Creating the EmClasses models with document inheritance
        for emclass in classes:
            emclass_fields = {
                'save' : self.get_save_fun(emclass.uniq_name, 'class', { 'classtype':emclass.classtype, 'class_name':emclass.uniq_name}),
            }

            #Addding non optionnal fields
            for emfield in emclass.fields():
                if not emfield.optional:
                    # !!! Replace with fieldtype 2 django converter
                    #emclass_fields[emfield.uniq_name] = models.CharField(max_length=56, default=emfield.uniq_name)
                    emclass_fields[emfield.uniq_name] = self.field_to_django(emfield, emclass)
            #print("Model for class %s created with fields : "%emclass.uniq_name, emclass_fields)
            print("Model for class %s created"%emclass.uniq_name)
            django_models['classes'][emclass.uniq_name] = create_model(emclass.uniq_name, emclass_fields, self.app_name, module_name, parent_class=django_models['doc'])
            
            #Creating the EmTypes models with EmClass inherithance
            for emtype in emclass.types():
                emtype_fields = {
                    'save': self.get_save_fun(emtype.uniq_name, 'type', { 'type_name':emtype.uniq_name }),
                }
                #Adding selected optionnal fields
                for emfield in emtype.selected_fields():
                    #emtype_fields[emfield.uniq_name] = models.CharField(max_length=56, default=emfield.uniq_name)
                    emtype_fields[emfield.uniq_name] = self.field_to_django(emfield, emtype)
                #Adding superiors foreign key
                for nature, superior in emtype.superiors().items():
                    emtype_fields[nature] = models.ForeignKey(superior.uniq_name, related_name=emtype.uniq_name, null=True)

                if self.debug:
                    print("Model for type %s created"%emtype.uniq_name)
                django_models['types'][emtype.uniq_name] = create_model(emtype.uniq_name, emtype_fields, self.app_name, module_name, parent_class=django_models['classes'][emclass.uniq_name])

        self.models=django_models
        pass

    ## @brief Return a good django field type given a field
    # @param f EmField : an EmField object
    # @param assoc_comp EmComponent : The associated component (type or class)
    def field_to_django(self, f, assoc_comp):

        args = dict()
        args['null'] = f.nullable
        if not (f.default is None):
            args['default'] = f.default
        v_fun = f.validation_function(raise_e = ValidationError)
        if v_fun:
            args['validators'] = [v_fun]

        if f.ftype == 'char':
            args['max_length'] = f.max_length
            return models.CharField(**args)
        elif f.ftype == 'int':
            return models.IntegerField(**args)
        elif f.ftype == 'rel2type':

            if assoc_comp == None:
                raise RuntimeError("Rel2type field in a rel2type table is not allowed")
            #create first a throught model if there is data field associated with the relation
            kwargs = dict()

            relf_l = f.get_related_fields()
            if len(relf_l) > 0:
                through_fields = {}
                
                #The two FK of the through model
                through_fields[assoc_comp.name] = models.ForeignKey(assoc_comp.uniq_name)
                rtype = f.get_related_type()
                through_fields[rtype.name] = models.ForeignKey(rtype.uniq_name)

                for relf in relf_l:
                    through_fields[relf.name] = self.field_to_django(relf, None)

                #through_model_name = f.uniq_name+assoc_comp.uniq_name+'to'+rtype.uniq_name
                through_model_name = f.name+assoc_comp.name+'to'+rtype.name
                module_name = self.app_name+'models'
                #model created
                through_model = create_model(through_model_name, through_fields, self.app_name, module_name)
                kwargs['through'] = through_model_name
            
            print('WOW !')
            return models.ManyToManyField(f.get_related_type().uniq_name, **kwargs)
        else:
            raise NotImplemented("The conversion to django fields is not yet implemented for %s field type"%f.ftype)


        

