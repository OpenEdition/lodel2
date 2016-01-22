#-*- coding: utf-8 -*-

import importlib
import copy
import os.path

import EditorialModel
from EditorialModel import classtypes
from EditorialModel.model import Model
from EditorialModel.fieldtypes.generic import GenericFieldType
from leapi.lecrud import _LeCrud


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

    ## @brief Generate fieldtypes for concret classes
    # @param ft_dict dict : key = fieldname value = fieldtype __init__ args
    # @return (uid_fieldtypes, fieldtypes) designed to be printed in generated code
    def concret_fieldtypes(self, ft_dict):
        res_ft_l = list()
        res_uid_ft = None
        for fname, ftargs in ft_dict.items():
            if ftargs is None:
                res_ft_l.append('%s: None' % repr(fname))
            else:
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
                    res_uid_ft = "{ %s: %s }"%(repr(fname),constructor)
                else:
                    res_ft_l.append( '%s: %s'%(repr(fname), constructor) )
        return (res_uid_ft, res_ft_l)

    ## @brief Given a Model generate concrete instances of LeRel2Type classes to represent relations
    # @param model : the EditorialModel
    # @return python code
    def emrel2type_pycode(self, model):
        res_code = ""
        for field in [ f for f in model.components('EmField') if f.fieldtype == 'rel2type']:
            related = model.component(field.rel_to_type_id)
            src = field.em_class
            cls_name = _LeCrud.name2rel2type(src.name, related.name, field.name)
            relation_name = field.name

            attr_l = dict()
            for attr in [ f for f in model.components('EmField') if f.rel_field_id == field.uid]:
                attr_l[attr.name] = LeFactory.fieldtype_construct_from_field(attr)

            rel_code = """
class {classname}(LeRel2Type):
    _rel_attr_fieldtypes = {attr_dict}
    _superior_cls = {supcls}
    _subordinate_cls = {subcls}
    _relation_name = {relation_name}

""".format(
    classname = cls_name,
    attr_dict = "{" + (','.join(['\n    %s: %s' % (repr(f), v) for f,v in attr_l.items()])) + "\n}",
    supcls = _LeCrud.name2classname(src.name),
    subcls = _LeCrud.name2classname(related.name),
    relation_name = repr(relation_name),
)
            res_code += rel_code
        return res_code

    ## @brief Given a Model and an EmClass instances generate python code for corresponding LeClass
    # @param model Model : A Model instance
    # @param emclass EmClass : An EmClass instance from model
    # @return A string representing the python code for the corresponding LeClass child class
    def emclass_pycode(self, model, emclass):

        cls_fields = dict()
        cls_linked_types = dict() # Stores rel2type referenced by fieldname
        #Populating linked_type attr
        for rfield in [ f for f in emclass.fields() if f.fieldtype == 'rel2type']:
            fti = rfield.fieldtype_instance()
            cls_linked_types[rfield.name] = _LeCrud.name2classname(model.component(fti.rel_to_type_id).name)
        # Populating fieldtype attr
        for field in emclass.fields(relational = False):
            if field.name not in EditorialModel.classtypes.common_fields.keys() or not ( hasattr(field, 'immutable') and field.immutable):
                self.needed_fieldtypes |= set([field.fieldtype])
                cls_fields[field.name] = LeFactory.fieldtype_construct_from_field(field)
                fti = field.fieldtype_instance()
        ml_fieldnames = dict()
        for field in emclass.fields():
            if field.string.get() == '':
                field.string.set_default(field.name)
            ml_fieldnames[field.name] = field.string.dumps()

        return """
#Initialisation of {name} class attributes
{name}._fieldtypes = {ftypes}
{name}.ml_fields_strings = {fieldnames}
{name}._linked_types = {ltypes}
{name}._classtype = {classtype}
""".format(
            name = _LeCrud.name2classname(emclass.name),
            ftypes = "{" + (','.join(['\n    %s: %s' % (repr(f), v) for f, v in cls_fields.items()])) + "\n}",
            fieldnames = '{' + (','.join(['\n   %s: MlString(%s)' % (repr(f), v) for f,v in ml_fieldnames.items()])) + '\n}',
            ltypes = "{" + (','.join(['\n    %s: %s' % (repr(f), v) for f, v in cls_linked_types.items()])) + "\n}",

            classtype = repr(emclass.classtype),
        )

    ## @brief Given a Model and an EmType instances generate python code for corresponding LeType
    # @param model Model : A Model instance
    # @param emtype EmType : An EmType instance from model
    # @return A string representing the python code for the corresponding LeType child class
    def emtype_pycode(self, model, emtype):
        type_fields = list()
        type_superiors = list()
        for field in emtype.fields(relational=False):
            if not field.name in EditorialModel.classtypes.common_fields:
                type_fields.append(field.name)

        for nat, sup_l in emtype.superiors().items():
            type_superiors.append('%s: [%s]' % (
                repr(nat),
                ', '.join([_LeCrud.name2classname(sup.name) for sup in sup_l])
            ))

        return """
#Initialisation of {name} class attributes
{name}._fields = {fields}
{name}._superiors = {dsups}
{name}._leclass = {leclass}
""".format(
            name=_LeCrud.name2classname(emtype.name),
            fields=repr(type_fields),
            dsups='{' + (', '.join(type_superiors)) + '}',
            leclass=_LeCrud.name2classname(emtype.em_class.name)
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
from Lodel.utils.mlstring import MlString

import leapi
import leapi.lecrud
import leapi.leobject
import leapi.lerelation
from leapi.leclass import _LeClass
from leapi.letype import _LeType
"""

        result += """
import %s

""" % (datasource_cls.__module__)

        #Generating the code for LeObject class
        leobj_me_uid = dict()
        for comp in model.components('EmType') + model.components('EmClass'):
            leobj_me_uid[comp.uid] = _LeCrud.name2classname(comp.name)
        
        #Building the fieldtypes dict of LeObject
        common_fieldtypes = dict()
        for ftname, ftdef in EditorialModel.classtypes.common_fields.items():
            common_fieldtypes[ftname] = ftdef if 'immutable' in ftdef and ftdef['immutable'] else None
        (leobj_uid_fieldtype, leobj_fieldtypes) = self.concret_fieldtypes(common_fieldtypes)
        #Building the fieldtypes dict for LeRelation
        common_fieldtypes = dict()
        for ftname, ftdef in EditorialModel.classtypes.relations_common_fields.items():
            common_fieldtypes[ftname] = ftdef if 'immutable' in ftdef and ftdef['immutable'] else None
        (lerel_uid_fieldtype, lerel_fieldtypes) = self.concret_fieldtypes(common_fieldtypes)

        result += """
## @brief _LeCrud concret class
# @see leapi.lecrud._LeCrud
class LeCrud(leapi.lecrud._LeCrud):
    _datasource = {ds_classname}(**{ds_kwargs})
    _uid_fieldtype = None

## @brief _LeObject concret class
# @see leapi.leobject._LeObject
class LeObject(LeCrud, leapi.leobject._LeObject):
    _me_uid = {me_uid_l}
    _me_uid_field_names = ({class_id}, {type_id})
    _uid_fieldtype = {leo_uid_fieldtype}
    _leo_fieldtypes = {leo_fieldtypes}

## @brief _LeRelation concret class
# @see leapi.lerelation._LeRelation
class LeRelation(LeCrud, leapi.lerelation._LeRelation):
    _uid_fieldtype = {lerel_uid_fieldtype}
    _rel_fieldtypes = {lerel_fieldtypes}
    ## WARNING !!!! OBSOLETE ! DON'T USE IT
    _superior_field_name = {lesup_name}
    ## WARNING !!!! OBSOLETE ! DON'T USE IT
    _subordinate_field_name = {lesub_name}

class LeHierarch(LeRelation, leapi.lerelation._LeHierarch):
    pass

class LeRel2Type(LeRelation, leapi.lerelation._LeRel2Type):
    pass

class LeClass(LeObject, _LeClass):
    pass

class LeType(LeClass, _LeType):
    pass
""".format(
            ds_classname = datasource_cls.__module__ + '.' + datasource_cls.__name__,
            ds_kwargs = repr(datasource_args),
            me_uid_l = repr(leobj_me_uid),
            leo_uid_fieldtype = leobj_uid_fieldtype,
            leo_fieldtypes = '{\n\t' + (',\n\t'.join(leobj_fieldtypes))+ '\n\t}',
            lerel_fieldtypes = '{\n\t' + (',\n\t'.join(lerel_fieldtypes))+ '\n\t}',
            lerel_uid_fieldtype = lerel_uid_fieldtype,
            lesup_name = repr(classtypes.relation_superior),
            lesub_name = repr(classtypes.relation_subordinate),
            class_id = repr(classtypes.object_em_class_id),
            type_id = repr(classtypes.object_em_type_id),
        )

        emclass_l = model.components(EditorialModel.classes.EmClass)
        emtype_l = model.components(EditorialModel.types.EmType)

        #LeClass child classes definition
        for emclass in emclass_l:
            if emclass.string.get() == '':
                emclass.string.set_default(emclass.name)
            result += """
## @brief EmClass {name} LeClass child class
# @see leapi.leclass.LeClass
class {name}(LeClass, LeObject):
    _class_id = {uid}
    ml_string = MlString({name_translations})

""".format(
                name=_LeCrud.name2classname(emclass.name),
                uid=emclass.uid,
                name_translations = repr(emclass.string.__str__()),
            )
        #LeType child classes definition
        for emtype in emtype_l:
            if emtype.string.get() == '':
                emtype.string.set_default(emtype.name)
            result += """
## @brief EmType {name} LeType child class
# @see leobject::letype::LeType
class {name}(LeType, {leclass}):
    _type_id = {uid}
    ml_string = MlString({name_translations})

""".format(
                name=_LeCrud.name2classname(emtype.name),
                leclass=_LeCrud.name2classname(emtype.em_class.name),
                uid=emtype.uid,
                name_translations = repr(emtype.string.__str__()),
            )

        #Generating concret class of LeRel2Type
        result += self.emrel2type_pycode(model)

        #Set attributes of created LeClass and LeType child classes
        for emclass in emclass_l:
            result += self.emclass_pycode(model, emclass)
        for emtype in emtype_l:
            result += self.emtype_pycode(model, emtype)


        #Populating LeObject._me_uid dict for a rapid fetch of LeType and LeClass given an EM uid
        me_uid = {comp.uid: _LeCrud.name2classname(comp.name) for comp in emclass_l + emtype_l}
        result += """
## @brief Dict for getting LeClass and LeType child classes given an EM uid
LeObject._me_uid = %s""" % "{" + (', '.join(['%s: %s' % (k, v) for k, v in me_uid.items()])) + "}"
        result += "\n"
        
        heading = heading.format(needed_fieldtypes_list = ', '.join(self.needed_fieldtypes))
        result = heading + result

        del(self.needed_fieldtypes)
        return result
