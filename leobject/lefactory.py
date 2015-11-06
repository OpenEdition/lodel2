#-*- coding: utf-8 -*-

import importlib

import EditorialModel
from EditorialModel.model import Model
from EditorialModel.fieldtypes.generic import GenericFieldType


## @brief This class is designed to generated the leobject API given an EditorialModel.model
# @note Contains only static methods
#
# The name is not good but i've no other ideas for the moment
class LeFactory(object):

    output_file = 'dyn.py'
    modname = None

    def __init__(self):
        raise NotImplementedError("Not designed (yet?) to be implemented")

    ## @brief Return a LeObject child class given its name
    # @return a python class or False
    @staticmethod
    def leobj_from_name(name):
        if LeFactory.modname is None:
            modname = 'leobject.' + LeFactory.output_file.split('.')[0]
        else:
            modname = LeFactory.modname
        mod = importlib.import_module(modname)
        try:
            res = getattr(mod, name)
        except AttributeError:
            return False
        return res

    @classmethod
    def leobject(cls):
        return cls.leobj_from_name('LeObject')

    ## @brief Convert an EmType or EmClass name in a python class name
    # @param name str : The name
    # @return name.title()
    @staticmethod
    def name2classname(name):
        if not isinstance(name, str):
            raise AttributeError("Argument name should be a str and not a %s" % type(name))
        return name.title()

    ## @brief Return a call to a FieldType constructor given an EmField
    # @param emfield EmField : An EmField
    # @return a string representing the python code to instanciate a EmFieldType
    @staticmethod
    def fieldtype_construct_from_field(emfield):
        return '%s.EmFieldType(**%s)' % (
            GenericFieldType.module_name(emfield.fieldtype),
            repr(emfield._fieldtype_args),
        )

    ## @brief Given a Model and an EmClass instances generate python code for corresponding LeClass
    # @param model Model : A Model instance
    # @param emclass EmClass : An EmClass instance from model
    # @return A string representing the python code for the corresponding LeClass child class
    @staticmethod
    def emclass_pycode(model, emclass):
        cls_fields = dict()
        cls_linked_types = dict() #keys are LeType classnames and values are tuples (attr_fieldname, attr_fieldtype)
        #Populating linked_type attr
        for rfield in [ f for f in emclass.fields() if f.fieldtype == 'rel2type']:
            fti = rfield.fieldtype_instance()
            cls_linked_types[LeFactory.name2classname(model.component(fti.rel_to_type_id).name)] = [
                (f.name, LeFactory.fieldtype_construct_from_field(f)) for f in model.components('EmField') if f.rel_field_id == rfield.uid 
            ]
        # Populating fieldtype attr
        for field in emclass.fields(relational = False):
            cls_fields[field.name] = LeFactory.fieldtype_construct_from_field(field)
            fti = field.fieldtype_instance()

        return """
#Initialisation of {name} class attributes
{name}._fieldtypes = {ftypes}
{name}._linked_types = {ltypes}
{name}._classtype = {classtype}
""".format(
            name = LeFactory.name2classname(emclass.name),
            ftypes = "{" + (','.join(['\n    %s: %s' % (repr(f), v) for f, v in cls_fields.items()])) + "\n}",

            ltypes = '{'+ (','.join(
                [
                    '\n    {ltname}: {ltattr_list}'.format(
                        ltname = lt,
                        ltattr_list = '['+(', '.join([
                            '(%s, %s)'%(repr(ltname), ltftype) for ltname, ltftype in ltattr
                        ]))+']'
                    ) for lt, ltattr in cls_linked_types.items()
                ]))+'}',
            classtype = repr(emclass.classtype)
        )

    ## @brief Given a Model and an EmType instances generate python code for corresponding LeType
    # @param model Model : A Model instance
    # @param emtype EmType : An EmType instance from model
    # @return A string representing the python code for the corresponding LeType child class
    @staticmethod
    def emtype_pycode(model, emtype):
        type_fields = list()
        type_superiors = list()
        for field in emtype.fields(relational=False):
            type_fields.append(field.name)

        for nat, sup_l in emtype.superiors().items():
            type_superiors.append('%s: [%s]' % (
                repr(nat),
                ', '.join([LeFactory.name2classname(sup.name) for sup in sup_l])
            ))

        return """
#Initialisation of {name} class attributes
{name}._fields = {fields}
{name}._superiors = {dsups}
{name}._leclass = {leclass}
""".format(
            name=LeFactory.name2classname(emtype.name),
            fields=repr(type_fields),
            dsups='{' + (', '.join(type_superiors)) + '}',
            leclass=LeFactory.name2classname(emtype.em_class.name)
        )

    ## @brief Generate python code containing the LeObject API
    # @param backend_cls Backend : A model backend class
    # @param backend_args dict : A dict representing arguments for backend_cls instanciation
    # @param datasource_cls Datasource : A datasource class
    # @param datasource_args dict : A dict representing arguments for datasource_cls instanciation
    # @return A string representing python code
    @staticmethod
    def generate_python(backend_cls, backend_args, datasource_cls, datasource_args):
        model = Model(backend=backend_cls(**backend_args))

        result = ""
        #result += "#-*- coding: utf-8 -*-\n"
        #Putting import directives in result
        result += """## @author LeFactory

from EditorialModel.model import Model
from leobject.leobject import _LeObject
from leobject.leclass import LeClass
from leobject.letype import LeType
import EditorialModel.fieldtypes
"""

        result += """
import %s
import %s

""" % (backend_cls.__module__, datasource_cls.__module__)

        #Generating the code for LeObject class
        backend_constructor = '%s.%s(**%s)' % (backend_cls.__module__, backend_cls.__name__, repr(backend_args))
        leobj_me_uid = dict()
        for comp in model.components('EmType') + model.components('EmClass'):
            leobj_me_uid[comp.uid] = LeFactory.name2classname(comp.name)

        result += """
## @brief _LeObject concret class
# @see leobject::leobject::_LeObject
class LeObject(_LeObject):
    _model = Model(backend=%s)
    _datasource = %s(**%s)
    _me_uid = %s

""" % (backend_constructor, datasource_cls.__module__ + '.' + datasource_cls.__name__, repr(datasource_args), repr(leobj_me_uid))

        emclass_l = model.components(EditorialModel.classes.EmClass)
        emtype_l = model.components(EditorialModel.types.EmType)

        #LeClass child classes definition
        for emclass in emclass_l:
            result += """
## @brief EmClass {name} LeClass child class
# @see leobject::leclass::LeClass
class {name}(LeObject, LeClass):
    _class_id = {uid}

""".format(
                name=LeFactory.name2classname(emclass.name),
                uid=emclass.uid
            )
        #LeType child classes definition
        for emtype in emtype_l:
            result += """
## @brief EmType {name} LeType child class
# @see leobject::letype::LeType
class {name}(LeType, {leclass}):
    _type_id = {uid}

""".format(
                name=LeFactory.name2classname(emtype.name),
                leclass=LeFactory.name2classname(emtype.em_class.name),
                uid=emtype.uid
            )

        #Set attributes of created LeClass and LeType child classes
        for emclass in emclass_l:
            result += LeFactory.emclass_pycode(model, emclass)
        for emtype in emtype_l:
            result += LeFactory.emtype_pycode(model, emtype)

        #Populating LeObject._me_uid dict for a rapid fetch of LeType and LeClass given an EM uid
        me_uid = {comp.uid: LeFactory.name2classname(comp.name) for comp in emclass_l + emtype_l}
        result += """
## @brief Dict for getting LeClass and LeType child classes given an EM uid
LeObject._me_uid = %s""" % "{" + (', '.join(['%s: %s' % (k, v) for k, v in me_uid.items()])) + "}"
        result += "\n"
        return result
