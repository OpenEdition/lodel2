#-*- coding: utf-8 -*-

import importlib
import copy
import os.path

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


    def __init__(self, code_filename = 'leapi/dyn.py'):
        self._code_filename = code_filename
        self._dyn_file = os.path.basename(code_filename)
        self._modname = os.path.dirname(code_filename).strip('/').replace('/', '.') #Warning Windaube compatibility

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
    
    ## @brief Write generated code to a file
    # @todo better options/params for file creation
    def create_pyfile(self, model, datasource_cls, datasource_args):
        with open(self._code_filename, "w+") as dynfp:
            dynfp.write(self.generate_python(model, datasource_cls, datasource_args))

    ## @brief Given a Model and an EmClass instances generate python code for corresponding LeClass
    # @param model Model : A Model instance
    # @param emclass EmClass : An EmClass instance from model
    # @return A string representing the python code for the corresponding LeClass child class
    def emclass_pycode(self, model, emclass):

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
            self.needed_fieldtypes |= set([field.fieldtype])
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
    def emtype_pycode(self, model, emtype):
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
    # @param model EditorialModel.model.Model : An editorial model instance
    # @param datasource_cls Datasource : A datasource class
    # @param datasource_args dict : A dict representing arguments for datasource_cls instanciation
    # @return A string representing python code
    def generate_python(self, model, datasource_cls, datasource_args):
        self.needed_fieldtypes = set() #Stores the list of fieldtypes that will be used by generated code

        model = model

        result = ""
        #result += "#-*- coding: utf-8 -*-\n"
        #Putting import directives in result
        heading = """## @author LeFactory

import EditorialModel
from EditorialModel import fieldtypes
from EditorialModel.fieldtypes import {needed_fieldtypes_list}

import leapi
import leapi.lecrud
import leapi.leobject
from leapi.leclass import LeClass
from leapi.letype import LeType
"""

        result += """
import %s

""" % (datasource_cls.__module__)

        #Generating the code for LeObject class
        leobj_me_uid = dict()
        for comp in model.components('EmType') + model.components('EmClass'):
            leobj_me_uid[comp.uid] = LeFactory.name2classname(comp.name)
        
        #Building the fieldtypes dict of LeObject
        leobj_fieldtypes = list()
        leobj_uid_fieldtype = None
        for fname, ftargs in EditorialModel.classtypes.common_fields.items():
            ftargs = copy.copy(ftargs)
            fieldtype = ftargs['fieldtype']
            self.needed_fieldtypes |= set([fieldtype])
            del(ftargs['fieldtype'])

            constructor = '{ftname}.EmFieldType(**{ftargs})'.format(
                ftname = GenericFieldType.module_name(fieldtype),
                ftargs = ftargs,
            )
            if fieldtype == 'pk':
                #
                #       WARNING multiple PK not supported
                #
                leobj_uid_fieldtype = constructor
            else:
                leobj_fieldtypes.append( '%s: %s'%(repr(fname), constructor) )
            

        result += """
## @brief _LeCrud concret class
# @see leapi.lecrud._LeCrud
class LeCrud(leapi.lecrud._LeCrud):
    _datasource = {ds_classname}(**{ds_kwargs})
    _uid_fieldtype = None

## @brief _LeObject concret class
# @see leapi.leobject._LeObject
class LeObject(leapi.leobject._LeObject, LeCrud):
    _me_uid = {me_uid_l}
    _uid_fieldtype = {leo_uid_fieldtype}
    _leo_fieldtypes = {leo_fieldtypes}

""".format(
            ds_classname = datasource_cls.__module__ + '.' + datasource_cls.__name__,
            ds_kwargs = repr(datasource_args),
            me_uid_l = repr(leobj_me_uid),
            leo_uid_fieldtype = leobj_uid_fieldtype,
            leo_fieldtypes = '{\n\t' + (',\n\t'.join(leobj_fieldtypes))+ '\n\t}',
        )

        emclass_l = model.components(EditorialModel.classes.EmClass)
        emtype_l = model.components(EditorialModel.types.EmType)

        #LeClass child classes definition
        for emclass in emclass_l:
            result += """
## @brief EmClass {name} LeClass child class
# @see leapi.leclass.LeClass
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
            result += self.emclass_pycode(model, emclass)
        for emtype in emtype_l:
            result += self.emtype_pycode(model, emtype)

        #Populating LeObject._me_uid dict for a rapid fetch of LeType and LeClass given an EM uid
        me_uid = {comp.uid: LeFactory.name2classname(comp.name) for comp in emclass_l + emtype_l}
        result += """
## @brief Dict for getting LeClass and LeType child classes given an EM uid
LeObject._me_uid = %s""" % "{" + (', '.join(['%s: %s' % (k, v) for k, v in me_uid.items()])) + "}"
        result += "\n"
        
        heading = heading.format(needed_fieldtypes_list = ', '.join(self.needed_fieldtypes))
        result = heading + result

        del(self.needed_fieldtypes)
        return result
