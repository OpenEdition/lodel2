#-*- coding: utf-8 -*-

import EditorialModel
from EditorialModel.model import Model
from EditorialModel.fieldtypes.generic import GenericFieldType

## @brief The factory that will return LeObject childs instances
#
# The name is not good but i've no other ideas for the moment
class LeFactory(object):
    
    def __init__(self):raise NotImplementedError("Not designed (yet?) to be implemented")

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
            fieldgroups = emclass.fieldgroups()
            for fieldgroup in fieldgroups:
                cls_fields[fieldgroup.name] = dict()
                for field in fieldgroup.fields():
                    fieldtype_constructor = '%s.EmFieldType(**%s)'%(
                        GenericFieldType.module_name(field.fieldtype),
                        field._fieldtype_args.__repr__(),
                    )
                    cls_fields[fieldgroup.name][field.name] = fieldtype_constructor
            
            result += "\n\
class %s(LeObject, LeClass):\n\
    _cls_fields = %s\n\
\n\
"%(emclass.name.title(), cls_fields.__repr__())

        for emtype in model.components(EditorialModel.types.EmType):
            type_fields = dict()
            fieldgroups = emtype.fieldgroups()
            for fieldgroup in fieldgroups:
                type_fields[fieldgroup.name] = dict()
                for field in fieldgroup.fields(emtype.uid):
                    fieltype_constructor = '%s.EmFieldType(**%s)'%(
                        GenericFieldType.module_name(field.fieldtype),
                        field._fieldtype_args.__repr__(),
                    )
                    type_fields[fieldgroup.name][field.name] = fieldtype_constructor

            result += "\n\
class %s(%s,LeType):\n\
    _fields = %s\n\
    _leClass = %s\n\
\n\
"%(emtype.name.title(), emtype.em_class.name.title(), type_fields.__repr__(), emtype.em_class.name.title())

        return result

