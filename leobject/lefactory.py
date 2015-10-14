#-*- coding: utf-8 -*-

import EditorialModel
from EditorialModel.model import Model
from EditorialModel.fieldtypes.generic import GenericFieldType

## @brief The factory that will return LeObject childs instances
#
# The name is not good but i've no other ideas for the moment
class LeFactory(object):
    
    def __init__(self):raise NotImplementedError("Not designed (yet?) to be implemented")

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
        result += "\n\
class LeObject(_LeObject):\n\
    _model = Model(backend=%s)\n\
    _datasource = %s(**%s)\n\
\n\
"%(backend_constructor, datasource_cls.__name__, datasource_args.__repr__())

        model = Model(backend=backend_cls(**backend_args))
        
        for emclass in model.components(EditorialModel.classes.EmClass):
            cls_fields = dict()
            for field in emclass.fields():
                cls_fields[field.name] = LeFactory.fieldtype_construct_from_field(field)
            cls_fieldgroup = dict()
            for fieldgroup in emclass.fieldgroups():
                cls_fieldgroup[fieldgroup.name] = list()
                for field in fieldgroup.fields():
                    cls_fieldgroup[fieldgroup.name].append(field.name)

            result += "\n\
class %s(LeObject, LeClass):\n\
    _fieldtypes = %s\n\
    _fieldgroups = %s\n\
\n\
"%(emclass.name.title(), cls_fields.__repr__(), cls_fieldgroup.__repr__())

        for emtype in model.components(EditorialModel.types.EmType):
            type_fields = list()
            for field in emtype.fields():
                type_fields.append(field.name)

            result += "\n\
class %s(%s,LeType):\n\
    _fields = %s\n\
    _leClass = %s\n\
\n\
"%(emtype.name.title(), emtype.em_class.name.title(), type_fields.__repr__(), emtype.em_class.name.title())

        return result

