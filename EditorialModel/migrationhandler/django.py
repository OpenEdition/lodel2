# -*- coding: utf-8 -*-

import django
from django.db import models
from django.contrib import admin

## @package EditorialModel.migrationhandler.django
# @brief A migration handler for django ORM
#
# Create django models according to the editorial model

##
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



class DjangoMigrationHandler(object):

    app_label = 'lodel'

    def __init__(self, debug=False):
        self.debug = debug

    def register_change(self, uid, initial_state, new_state):
        pass

    def register_model_state(self, state_hash):
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
    # @param me EditorialModel.model.Model : The editorial model instance
    # @return a dict with all the models
    # @todo Handle fieldgroups
    # @todo write and use a function to forge models name from EmClasses and EmTypes names
    # @note There is a problem with the related_name for superiors fk : The related name cannot be subordinates, it has to be the subordinates em_type name
    def me_to_models(self, me, app_label, module_name):
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
        document_model = create_model('document', document_attrs, app_label, module_name)

        django_models = {'doc' : document_model, 'classes':{}, 'types':{} }

        classes = me.classes()

        #Creating the EmClasses models with document inheritance
        for emclass in classes:
            emclass_fields = {
                'save' : self.get_save_fun(emclass.name, 'class', { 'classtype':emclass.classtype, 'class_name':emclass.name})
            }

            #Addding non optionnal fields
            for emfield in emclass.fields():
                if not emfield.optional:
                    # !!! Replace with fieldtype 2 django converter
                    emclass_fields[emfield.name] = models.CharField(max_length=56, default=emfield.name)
            print("Model for class %s created with fields : "%emclass.name, emclass_fields)
            django_models['classes'][emclass.name] = create_model(emclass.name, emclass_fields, app_label, module_name, parent_class=django_models['doc'])
            
            #Creating the EmTypes models with EmClass inherithance
            for emtype in emclass.types():
                emtype_fields = {
                    'save': self.get_save_fun(emtype.name, 'type', { 'type_name':emtype.name }),

                }
                #Adding selected optionnal fields
                for emfield in emtype.selected_fields():
                    emtype_fields[emfield.name] = models.CharField(max_length=56, default=emfield.name)
                #Adding superiors foreign key
                for nature, superior in emtype.superiors().items():
                    emtype_fields[nature] = models.ForeignKey(superior.name, related_name=emtype.name, null=True)

                print("Model for type %s created with fields : "%emtype.name, emtype_fields)
                django_models['types'][emtype.name] = create_model(emtype.name, emtype_fields, app_label, module_name, parent_class=django_models['classes'][emclass.name])

        return django_models


