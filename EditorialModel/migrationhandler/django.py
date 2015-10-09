# -*- coding: utf-8 -*-

import os
import sys

import django
from django.db import models
from django.db.models.loading import cache as django_cache
from django.core.exceptions import ValidationError
from django.contrib import admin
from EditorialModel.migrationhandler.dummy import DummyMigrationHandler
from EditorialModel.classtypes import EmNature

from EditorialModel.exceptions import *


## @brief Create a django model
# @param name str : The django model name
# @param fields dict : A dict that contains fields name and type ( str => DjangoField )
# @param app_label str : The name of the applications that will have those models
# @param module str : The module name this model will belong to
# @param options dict : Dict of options (name => value)
# @param admin_opts dict : Dict of options for admin part of this model
# @param parent_class str : Parent class name
# @return A dynamically created django model
# @note Source : https://code.djangoproject.com/wiki/DynamicModels
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
    attrs = {'__module__': module, 'Meta': Meta}

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

class DjangoMigrationHandler(DummyMigrationHandler):

    ## @brief Instanciate a new DjangoMigrationHandler
    # @param app_name str : The django application name for models generation
    # @param debug bool : Set to True to be in debug mode
    # @param dryrun bool : If true don't do any migration, only simulate them
    def __init__(self, app_name, debug=False, dryrun=False):
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
    # @param uid int : The EmComponent uid
    # @param initial_state dict | None : dict representing the fields that are changing
    # @param new_state dict | None : dict represnting the new fields states
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
            raise MigrationHandlerChangeError("Unable to migrate to new model state : %s" % e)

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
    @staticmethod
    def set_save_fun(class_obj, level, datas):

        if level == 'class':
            def save(self, *args, **kwargs):
                #Sets the classtype and class name
                self.classtype = datas['classtype']
                self.class_name = datas['class_name']
                super(class_obj, self).save(*args, **kwargs)
        elif level == 'type':
            def save(self, *args, **kwargs):
                #Set the type name
                self.type_name = datas['type_name']
                super(class_obj, self).save(*args, **kwargs)

        class_obj.save = save

        return class_obj

    ## @brief Create django models from an EditorialModel.model object
    # @param edMod EditorialModel.model.Model : The editorial model instance
    # @return a dict with all the models
    # @todo Handle fieldgroups
    # @todo write and use a function to forge models name from EmClasses and EmTypes names
    # @note There is a problem with the related_name for superiors fk : The related name cannot be subordinates, it has to be the subordinates em_type name
    def em_to_models(self, edMod):

        module_name = self.app_name + '.models'

        #Purging django models cache
        if self.app_name in django_cache.all_models:
            for modname in django_cache.all_models[self.app_name]:
                del(django_cache.all_models[self.app_name][modname])
            #del(django_cache.all_models[self.app_name])

        app_name = self.app_name
        #Creating the document model
        document_attrs = {
            'lodel_id': models.AutoField(primary_key=True),
            'classtype': models.CharField(max_length=16, editable=False),
            'class_name': models.CharField(max_length=76, editable=False),
            'type_name': models.CharField(max_length=76, editable=False),
            'string': models.CharField(max_length=255),
            'date_update': models.DateTimeField(auto_now=True, auto_now_add=True),
            'date_create': models.DateTimeField(auto_now_add=True),
            'rank': models.IntegerField(),
            'help_text': models.CharField(max_length=255),
        }

        #Creating the base model document
        document_model = create_model('document', document_attrs, self.app_name, module_name)

        django_models = {'doc': document_model, 'classes': {}, 'types': {}}

        classes = edMod.classes()

        def object_repr(self):
            return self.string

        #Creating the EmClasses models with document inheritance
        for emclass in classes:
            emclass_fields = {
                'save': None, #will be set later using self.set_save_fun
                '__str__': object_repr,
            }

            #Addding non optionnal fields
            for emfield in emclass.fields():
                if not emfield.optional:
                    # !!! Replace with fieldtype 2 django converter
                    #emclass_fields[emfield.uniq_name] = models.CharField(max_length=56, default=emfield.uniq_name)
                    emclass_fields[emfield.uniq_name] = self.field_to_django(emfield, emclass)
            #print("Model for class %s created with fields : "%emclass.uniq_name, emclass_fields)
            if self.debug:
                print("Model for class %s created" % emclass.uniq_name)
            django_models['classes'][emclass.uniq_name] = create_model(emclass.uniq_name, emclass_fields, self.app_name, module_name, parent_class=django_models['doc'])

            self.set_save_fun(django_models['classes'][emclass.uniq_name], 'class', {'classtype': emclass.classtype, 'class_name': emclass.uniq_name})


            #Creating the EmTypes models with EmClass inherithance
            for emtype in emclass.types():
                emtype_fields = {
                    'save':None,
                    '__str__': object_repr,
                }
                #Adding selected optionnal fields
                for emfield in emtype.selected_fields():
                    #emtype_fields[emfield.uniq_name] = models.CharField(max_length=56, default=emfield.uniq_name)
                    emtype_fields[emfield.uniq_name] = self.field_to_django(emfield, emtype)
                #Adding superiors foreign key
                for nature, superiors_list in emtype.superiors().items():
                    for superior in superiors_list:
                        emtype_fields[nature+'_'+superior.uniq_name] = models.ForeignKey(superior.uniq_name, related_name=emtype.uniq_name, blank=True, default=None, null=True)
                    
                    # Method to get the parent that is not None
                    emtype_fields['sup_field_list'] = [ nature + '_' + superior.uniq_name for superior in superiors_list ]
                    def get_sup(self):
                        for field in [ getattr(self, fname) for fname in self.sup_field_list ]:
                            if not (field is None):
                                return field
                        return None
                    #Adding a method to get the superior by nature
                    emtype_fields[nature] = get_sup
                
                # Adding a dummy function to non present nature
                def dummyNone(self): return None
                for nat in [ nat for nat in EmNature.getall() if nat not in emtype_fields]:
                    emtype_fields[nat] = dummyNone
                        

                if self.debug:
                    print("Model for type %s created" % emtype.uniq_name)
                django_models['types'][emtype.uniq_name] = create_model(emtype.uniq_name, emtype_fields, self.app_name, module_name, parent_class=django_models['classes'][emclass.uniq_name], admin_opts=dict())
                self.set_save_fun(django_models['types'][emtype.uniq_name], 'type', {'type_name': emtype.uniq_name})
        return django_models

    ## @brief Return a good django field type given a field
    # @param f EmField : an EmField object
    # @param assoc_comp EmComponent : The associated component (type or class)
    # @return A django field instance
    # @note The manytomany fields created with the rel2type field has no related_name associated to it
    def field_to_django(self, f, assoc_comp):

        #Building the args dictionnary for django field instanciation
        args = dict()
        args['null'] = f.nullable
        if not (f.default is None):
            args['default'] = f.default
        v_fun = f.validation_function(raise_e=ValidationError)
        if v_fun:
            args['validators'] = [v_fun]
        if f.uniq:
            args['unique'] = True

        # Field instanciation
        if f.ftype == 'char':  # varchar field
            args['max_length'] = f.max_length
            return models.CharField(**args)
        elif f.ftype == 'int':  # integer field
            return models.IntegerField(**args)
        elif f.ftype == 'text':  # text field
            return models.TextField(**args)
        elif f.ftype == 'datetime':  # Datetime field
            args['auto_now'] = f.now_on_update
            args['auto_now_add'] = f.now_on_create
            return models.DateTimeField(**args)
        elif f.ftype == 'bool':  # Boolean field
            if args['null']:
                return models.NullBooleanField(**args)
            del(args['null'])
            return models.BooleanField(**args)
        elif f.ftype == 'rel2type':  # Relation to type

            if assoc_comp is None:
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
                through_model_name = f.name + assoc_comp.name + 'to' + rtype.name
                module_name = self.app_name + '.models'
                #model created
                through_model = create_model(through_model_name, through_fields, self.app_name, module_name)
                kwargs['through'] = through_model_name

            return models.ManyToManyField(f.get_related_type().uniq_name, **kwargs)
        else:  # Unknow data type
            raise NotImplemented("The conversion to django fields is not yet implemented for %s field type" % f.ftype)
