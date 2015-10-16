#-*- coding: utf-8 -*-

import importlib

import EditorialModel
from EditorialModel.model import Model
from EditorialModel.fieldtypes.generic import GenericFieldType

## @brief The factory that will return LeObject childs instances
#
# The name is not good but i've no other ideas for the moment
class LeFactory(object):
    
    output_file = 'dyn.py'

    def __init__(LeFactory):raise NotImplementedError("Not designed (yet?) to be implemented")

    ## @brief Return a LeObject child class given its name
    # @return a python class or False
    @staticmethod
    def leobj_from_name(name):
        mod = importlib.import_module('leobject.'+LeFactory.output_file.split('.')[-1])
        try:
            res = getattr(mod, name)
        except AttributeError:
            return False
        return res

    ## @brief Convert an EmType or EmClass name in a python class name
    # @param name str : The name
    # @return name.title()
    @staticmethod
    def name2classname(name):
        return name.title()

    ## @brief Return a call to a FieldType constructor given an EmField
    # @param emfield EmField : An EmField
    # @return a string representing the python code to instanciate a EmFieldType
    @staticmethod
    def fieldtype_construct_from_field(emfield):    
        return '%s.EmFieldType(**%s)'%(
            GenericFieldType.module_name(emfield.fieldtype),
            emfield._fieldtype_args.__repr__(),
        )
            
        
    ## @brief Generate python code containing the LeObject API
    # @param model_args dict : Dict of Model __init__ method arguments
    # @param datasource_args dict : Dict of datasource __init__ method arguments
    # @return A string representing python code
    @staticmethod
    def generate_python(backend_cls, backend_args, datasource_cls, datasource_args):
        model = Model(backend=backend_cls(**backend_args))

        result = ""
        result += "#-*- coding: utf-8 -*-\n"
        #Putting import directives in result
        result += "\n\n\
from EditorialModel.model import Model\n\
from leobject.leobject import _LeObject\n\
from leobject.leclass import LeClass\n\
from leobject.letype import LeType\n\
import EditorialModel.fieldtypes\n\
"

        result += "\n\
import %s\n\
import %s\n\
"%(backend_cls.__module__, datasource_cls.__module__)

        #Generating the code for LeObject class
        backend_constructor = '%s.%s(**%s)'%(backend_cls.__module__, backend_cls.__name__, backend_args.__repr__())
        leobj_me_uid = dict()
        for comp in model.components('EmType') + model.components('EmClass'):
            leobj_me_uid[comp.uid] = LeFactory.name2classname(comp.name)

        result += "\n\
class LeObject(_LeObject):\n\
    _model = Model(backend=%s)\n\
    _datasource = %s(**%s)\n\
    _me_uid = %s\n\
\n\
"%(backend_constructor, datasource_cls.__name__, datasource_args.__repr__(), leobj_me_uid.__repr__())
        
        for emclass in model.components(EditorialModel.classes.EmClass):
            cls_fields = dict()
            cls_linked_types = list()
            for field in emclass.fields():
                cls_fields[field.name] = LeFactory.fieldtype_construct_from_field(field)
                fti = field.fieldtype_instance()
                if fti.name == 'rel2type':
                    #relationnal field/fieldtype
                    cls_linked_types.append(LeFactory.name2classname(model.component(fti.rel_to_type_id).name))
            cls_fieldgroup = dict()
            for fieldgroup in emclass.fieldgroups():
                cls_fieldgroup[fieldgroup.name] = list()
                for field in fieldgroup.fields():
                    cls_fieldgroup[fieldgroup.name].append(field.name)

            result += "\n\
class %s(LeObject, LeClass):\n\
    _fieldtypes = %s\n\
    _linked_types = [%s]\n\
    _fieldgroups = %s\n\
\n\
"%(
    LeFactory.name2classname(emclass.name),
    cls_fields.__repr__(),
    ','.join(cls_linked_types),
    cls_fieldgroup.__repr__()
)

        for emtype in model.components(EditorialModel.types.EmType):
            type_fields = list()
            type_superiors = list()
            for field in emtype.fields():
                type_fields.append(field.name)

            for nat, sup_l in emtype.superiors().items():
                type_superiors.append('%s:[%s]'%(
                    nat.__repr__(),
                    ','.join([ LeFactory.name2classname(sup.name) for sup in sup_l])
                ))


            result += "\n\
class %s(%s,LeType):\n\
    _fields = %s\n\
    _superiors = {%s}\n\
    _leClass = %s\n\
\n\
"%(
    LeFactory.name2classname(emtype.name),
    LeFactory.name2classname(emtype.em_class.name),
    type_fields.__repr__(),
    ','.join(type_superiors),
    LeFactory.name2classname(emtype.em_class.name)
)

        return result

