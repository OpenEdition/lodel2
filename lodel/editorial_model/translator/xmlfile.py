#-*- coding: utf-8 -*-

import lxml
import os
from lxml import etree

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.editorial_model.model': ['EditorialModel'],
    'lodel.editorial_model.components': ['EmComponent', 'EmClass', 'EmField',
        'EmGroup'],
    'lodel.utils.mlstring': ['MlString']})

## @package lodel.editorial_model.translator.xmlfile
# This module is a translator toolkit between and editorial model and an XML file.
#
# The XML file representing an editorial is composed by several nodes.
#
# @par \<name\>
# The name of the model. It matches with the <b><em>name</em></b> field of the <b><em>EditorialModel class</em></b>
#
# @par \<description\>
# This is the description of a composed element. Inside this node, we can have as many child node as there are languages in which it is translated. \n
# Each translation is notified by a node, using the following scheme :
# <ul>
#   <li><b>\<fre\></b> : french
#   <li><b>\<eng\></b> : english
#   <li><b>\<esp\></b> : spanish
#   <li><b>\<ger\></b> : german
# </ul>
#
# @par \<classes\>
# This node contains a set of all the <b><em>EmClass</em></b> classes we can find in the model, each represented by a <b>\<class\></b> child node.
#
# @par \<class\>
# It is the representation of a single <b><em>EmClass</em></b> class. It is contained in the <b><em>\<classes\></em></b> node. It contains the following child nodes :
# <ul>
# <li><b>\<uid\></b> : The identifier of the class.
# <li><b>\<display_name\></b> : The class' name, given by the <b><em>display_name</em></b> field of the <b><em>EmClass</em></b> class. This node contains the same language child nodes as the \<description\> node.
# <li><b>\<help_text\></b> : A short description of the purpose of this class, using the same child nodes for each language, as above.
# <li><b>\<abstract\></b> : Boolean node, with True or False as values, corresponding to the field <b><em>abstract</em></b> of the <b><em>EmClass</em></b> object.
# <li><b>\<abstract\></b> : Boolean node, with True or False as values, corresponding to the field <b><em>pure_abstract</em></b> of the <b><em>EmClass</em></b> object.
# <li><b>\<group\></b> : The unique identifier of the group stored in the <b><em>group</em></b> field of the <b><em>EmClass</em></b> object.
# <li><b>\<fields\></b> : A set of all the <b><em>EmField</em></b> fields attached to an <b></em>EmClass</em></b> class. Each of them is represented by a <b>\<field\></b> child node.
# </ul>
#
# @par \<field\>
# This node is the XML representation of an <b><em>EmField</em></b> class. It contains the following child nodes :
# <ul>
# <li><b>\<uid\></b> : The identifier of the field.
# <li><b>\<display_name\></b> : Displayed name, in different languages (same child nodes as above), corresponding to the <b><em>display_name</em></b> property of the <b><em>EmField</em></b>.
# <li><b>\<help_text\></b> : Short explanation of the purpose of the field, in different languages (one child node for each translation, see above).
# <li><b>\<group\></b> : <b><em>uid</em></b> of the group of the field <b><em>group</em></b> in the <b><em>EmField</em></b>
# <li><b>\<datahandler_name\></b> : The name of the datahandler attached to this field (corresponds to the field <b><em>datahandler_name</em></b> of the Emfield)
# <li><b>\<datahandler_options\></b> : A list of xml items, each of them named with an option name and containing its value
# </ul>
#
# @par \<groups\>
# This node contains a set of all the groups in the model (represented by <b><em>EmGroup</em></b> objects) with a <b>\<group\></b> child node for each one.
#
# @par \<group\>
# Represents a single group. This node contains the following child nodes :
# <ul>
# <li><b>\<uid\></b> : unique id of the <b><em>EmField</em></b>.
# <li><b>\<display_name\></b> : Corresponds to the <b><em>display_name</em></b>  property of the <b><em>EmField</em></b>, in different languages (see above)
# <li><b>\help_text\></b> : Short explanation of the group's purpose, in different languages (see above)
# <li><b>\<requires\></b> : All the unique identifiers of the <b><em>EmGroups</em></b> required by this group and which are in the fields <b><em>require</em></b>.
# <li><b>\<components\></b> : A set of all components of the <b><em>EmGroups</em></b>, representation of the field <b><em>__components</em></b>. This node is splitted in two parts :
#     <ul>
#         <li><b>\<emfields\></b> : all the emfields with, for each of them:\n
#               <b>\<emfield\></b> \n
#                  <b>\<uid\></b> : <b><em>uid</em></b> of the <b><em>EmField</em></b>
#           <li><b>\<emclasses\></b> : all the emclasses with, for each of them:\n
#               <b>\<emclass\></b> \n
#                  <b>\<uid\></b> : <b><em>uid</em></b> of the <b><em>EmClass</em></b>
#     </ul>
# </ul>


## @brief Saves a model in a XML file
# @param model EditorialModel : the model to save
# @param kwargs dict : additional options.
#                     - filename str|None : if None display on stdout else writes in the file filename
def save(model, **kwargs):
    Em = etree.Element("editorial_model")
    em_name = etree.SubElement(Em, 'name')
    write_mlstring_xml(etree, em_name, model.name)
    
    em_description = etree.SubElement(Em, 'description')
    write_mlstring_xml(etree, em_description, model.description)
    
    em_classes = etree.SubElement(Em, 'classes')
    classes = model.all_classes()
    for emclass in classes:
        write_emclass_xml(etree, em_classes, classes[emclass].uid, classes[emclass].display_name, 
                          classes[emclass].help_text, classes[emclass].group, 
                          classes[emclass].fields(no_parents=True), classes[emclass].parents, 
                          classes[emclass].abstract, classes[emclass].pure_abstract)

    em_groups = etree.SubElement(Em, 'groups')
    groups = model.all_groups()
    for group in groups:
        requires = groups[group].dependencies()
        write_emgroup_xml(etree, em_groups, groups[group].uid, groups[group].display_name, groups[group].help_text, 
                          list(requires.keys()), groups[group].components())
        
    emodel = etree.tostring(Em, encoding='utf-8',  xml_declaration=True, method='xml', pretty_print= True)
    if len(kwargs) == 0:
        print(emodel.decode())
    else:
        outfile = open(kwargs['filename'], "w")
        outfile.write(emodel.decode())
        outfile.close()
    
    
## @brief Writes a representation of a MlString in XML
# @param etree Element : the XML object
# @param elem Element : the element which represents a MlString
# @param mlstr MlString: the mlstr to write
def write_mlstring_xml(etree, elem, mlstr):
    for lang in mlstr.values:
        ss_mlstr = etree.SubElement(elem,lang)
        ss_mlstr.text = mlstr.get(lang)
        
## @brief Writes the definition of a datahandler in xml
# @param etree : the xml object
# @param elem Element : the element which defines a datahandler
# @param dhdl_name str : the name of the datahandler
# @param kwargs : the options of the datahandler
def write_datahandler_xml(etree, elem, dhdl_name, **kwargs):
    dhdl = etree.SubElement(elem,'datahandler_name')
    dhdl.text = dhdl_name
    dhdl_opt = etree.SubElement(elem, 'datahandler_options')

    for argname, argval in kwargs.items():
        arg = etree.SubElement(dhdl_opt, argname)
        opt_val=''
        if (isinstance(argval, str)):
            opt_val=argval
        elif (isinstance(argval, bool)):
            opt_val = str(argval)
        elif (isinstance(argval, list) | isinstance(argval, tuple) | isinstance(argval, dict)):
            for argu in argval:
                if len(opt_val) > 0:
                    opt_val = opt_val + ','
                if isinstance(argu, EmComponent):
                    opt_val = opt_val + argu.uid
                elif isinstance(argu, str):
                    opt_val = opt_val + argu
                else:
                    opt_val = str(argu)
        arg.text = opt_val
        
## @brief Writes a representation in xml of a EmField
# @param etree : the xml object
# @param elem Element: the element for the EmField
# @param uid str : the uid of the EmField
# @param name str : the name of the field
# @param help_text MlString: explanations of the EmField
# @param group str|None: the uid of a group, can be None
# @param datahandler_name str: Name of the datahandler attached to the field
# @param **kwargs dict : options of the datahandler
def write_emfield_xml(etree, elem, uid, name, help_text, group, datahandler_name, **kwargs):
    emfield = etree.SubElement(elem,'field')
    emfield_uid = etree.SubElement(emfield, 'uid')
    emfield_uid.text = uid
    emfield_name = etree.SubElement(emfield, 'display_name')
    if name is None:
        pass
    else:
        write_mlstring_xml(etree, emfield_name, name)
    emfield_help = etree.SubElement(emfield, 'help_text')
    if help_text is None:
        pass
    else:
        write_mlstring_xml(etree, emfield_help, help_text)
    emfield_group = etree.SubElement(emfield, 'group')

    if group is not None:
        emfield_group.text = group.uid #write_emgroup_xml(etree, emfield_group, group.uid, group.display_name, group.help_text, group.requires)
    write_datahandler_xml(etree,emfield,datahandler_name, **kwargs)

##@brief Writes a representation of a EmGroup in xml
# @param etree : the xml object
# @param elem Element : the element for the EmGroup
# @param uid str : the uid of the EmGroup
# @param name str : the name of the group
# @param help_text MlString : explanations of the EmGroup
# @param requires list : a list of the group's uids whose this group depends
# @param components list : a list of the EmComponent objects contained in the group
def write_emgroup_xml(etree, elem, uid, name, help_text, requires, components):
    emgroup = etree.SubElement(elem, 'group')
    emgroup_uid = etree.SubElement(emgroup, 'uid')
    emgroup_uid.text = uid
    emgroup_name = etree.SubElement(emgroup, 'display_name')
    if name is None:
        pass
    else:
        write_mlstring_xml(etree, emgroup_name, name)
    emgroup_help = etree.SubElement(emgroup, 'help_text')
    if help_text is None:
        pass
    else:
        write_mlstring_xml(etree, emgroup_help, help_text)
    emgroup_requires = etree.SubElement(emgroup, 'requires')
    emgroup_requires.text = ",".join(requires)
    emgroup_comp = etree.SubElement(emgroup, 'components')
    emgroup_comp_cls = etree.SubElement(emgroup_comp, 'emclasses')
    emgroup_comp_fld = etree.SubElement(emgroup_comp, 'emfields')
    
    for component in components:
        if isinstance(component, EmField):
            emgroup_comp_fld_ins = etree.SubElement(emgroup_comp_fld, 'emfield')
            em_group_comp_fld_ins_uid =  etree.SubElement(emgroup_comp_fld_ins,'uid')
            em_group_comp_fld_ins_uid.text = component.uid
            em_group_comp_fld_ins_cls = etree.SubElement(emgroup_comp_fld_ins,'class')
            em_group_comp_fld_ins_cls.text = component.get_emclass_uid()
        elif isinstance(component, EmClass):
            em_group_comp_cls_ins = etree.SubElement(emgroup_comp_cls, 'emclass')
            em_group_comp_cls_ins.text = component.uid

## @brief Writes a representation of a EmClass in XML
# @param etree : the XML object
# @param elem Element : the element for the EmClass
# @param uid str : the unique identifier of the EmClass
# @param name str : the name of the group
# @param help_text MlString : explanations of the EmClass
# @param fields dict : a dict representing all the fields of the class
# @param parents list : a list of the EmClass uids of this class' parents
# @param abstract bool : a boolean
# @param pure_abstract bool : a boolean
def write_emclass_xml(etree, elem, uid, name, help_text, group, fields, parents, abstract = False, pure_abstract = False):
    emclass = etree.SubElement(elem, 'class')
    emclass_uid  = etree.SubElement(emclass, 'uid')
    emclass_uid.text = uid
    emclass_name = etree.SubElement(emclass, 'display_name')
    if name is None:
        pass
    else:
        write_mlstring_xml(etree, emclass_name, name)
    emclass_help = etree.SubElement(emclass, 'help_text')
    if help_text is None:
        pass
    else:
        write_mlstring_xml(etree, emclass_help, help_text)
    emclass_abstract = etree.SubElement(emclass, 'abstract')
    emclass_abstract.text ="True" if abstract else "False"
    emclass_pure_abstract = etree.SubElement(emclass, 'pure_abstract')
    emclass_pure_abstract.text = "True" if pure_abstract else "False"
    emclass_group = etree.SubElement(emclass, 'group')
    if group is not None:
        emclass_group.text = group.uid
    emclass_fields = etree.SubElement(emclass, 'fields')
    for field in fields:
        write_emfield_xml(etree, emclass_fields, field.uid, field.display_name, field.help_text, 
                          field.group,field.data_handler_name, **field.data_handler_options)
    parents_list=list()
    for parent in parents:
        parents_list.append(parent.uid)
    emclass_parents = etree.SubElement(emclass, 'parents')
    emclass_parents.text = ",".join(parents_list)

## @brief Loads a model from a XML file
# @param filename str : The file from which the editorial model will be loaded
# @return a new EditorialModel object
def load(filename):
    Em = etree.parse(filename)
    emodel = Em.getroot()
    name = emodel.find('name')
    description = emodel.find('description')

    model = EditorialModel(load_mlstring_xml(name), load_mlstring_xml(description))
        
    classes = emodel.find('classes')
    for emclass in classes:
        em_class = load_class_xml(model, emclass)
        if em_class.uid not in model.all_classes():
            model.add_class(em_class)
    
    groups = emodel.find('groups')
    i = 0
    for group in groups:
        grp = load_group_xml(model, group)
        if grp.uid not in model.all_groups():
            grp = model.add_group(grp)
    return model


## @brief Creates a EmClass from a xml description
# @param model EditorialModel : the model which will contain the new class
# @param elem Element: the element which represents the EmClass
# @return a new EmClass object
def load_class_xml(model, elem):
    uid = elem.find('uid').text
    if elem.find('display_name').text is None:
        name = None
    else:
        name = load_mlstring_xml(elem.find('display_name'))
    if elem.find('help_text').text is None:
        help_text = None
    else:
        help_text = load_mlstring_xml(elem.find('help_text'))
        
    abstract = (elem.find('abstract').text == 'True')
    pure_abstract = (elem.find('pure_abstract').text == 'True')
    requires = list()
    classes = model.all_classes()
    req = elem.find('parents')
    if req.text is not None:
        l_req = req.text.split(',')
        for r in l_req:
            if r in classes:
                requires.append(model.all_classes_ref(r))
            else:
                requires.append(model.add_class(EmClass(r)))
    group = elem.find('group')
    if group.text is not None:
        if group.text in model.all_groups():
            grp = model.all_groups_ref(group.text)
        else:
            grp = model.add_group(EmGroup(group.text))
    else:
        grp = None

    if uid in classes:
        emclass = model.all_classes_ref(uid)
        emclass.display_name = name
        emclass.help_text = help_text
        emclass.parents=requires
        emclass.group = grp
        emclass.abstract = abstract
        emclass.pure_abstract = pure_abstract
    else:
        emclass = EmClass(uid, name, help_text, abstract,requires, grp, pure_abstract)
        model.add_class(emclass)
        
    fields = elem.find('fields')
    for field in fields:
        emfield = load_field_xml(model, field, emclass)
        l_emfields = emclass.fields()
        incls = False
        for emf in l_emfields:
            if emfield.uid == emf.uid:
                incls = True
                break
        if not incls:
            emclass.add_field(emfield)
            
    return emclass
    
## @brief Creates a EmField from a XML description
# @param model EditorialModel: the model which will contain the new field
# @param elem Element : the element which represents the EmField
# @param emclass EmClass : the EmClass of the field
# @return a new EmField object
def load_field_xml(model, elem, emclass):
    uid = elem.find('uid').text
    if elem.find('display_name').text is None:
        name = None
    else:
        name = load_mlstring_xml(elem.find('display_name'))
        
    if elem.find('help_text').text is None:
        help_text = None
    else:
        help_text = load_mlstring_xml(elem.find('help_text'))
        
    emgroup = elem.find('group')
    if emgroup.text is not None:
        if emgroup.text in model.all_groups():
            group = model.all_groups_ref(emgroup.text)
        else:
            group = model.add_group(EmGroup(emgroup.text))
    else:
        group = None
        
    dhdl = elem.find('datahandler_name')
    dhdl_opts = {}
    if dhdl.text is not None:
        dhdl_opts = elem.find('datahandler_options')
        if dhdl_opts is not None:
            dhdl_options = load_dhdl_options_xml(model, dhdl_opts) 
    emfield = EmField(
        uid, dhdl.text, emclass, name, help_text, group, **dhdl_options)
    
    return emfield


## @brief Returns datahandler options from a XML description
# @param elem Element : the element which represents the datahandler
# @param model EditorialModel : the model which will contain the new field
# @return dict
def load_dhdl_options_xml(model, elem):
    dhdl_options=dict()
    for opt in elem:
        if (opt.tag == 'allowed_classes'):
            classes = list()
            if opt.text is not None:
                clss = opt.text.split(',')
                for classe in clss:
                    if classe in model.all_classes():
                        classes.append(model.all_classes_ref(classe))
                    else:
                        new_cls = model.add_class(EmClass(classe))
                        classes.append(new_cls)
            dhdl_options['allowed_classes'] = classes
        elif (opt.tag == 'back_reference'):
            dhdl_options['back_reference'] = tuple(opt.text.split(','))
        elif ((opt.text == 'True') | (opt.text == 'False')):
            dhdl_options[opt.tag] = (opt.text == 'True')
        else:
            dhdl_options[opt.tag] = opt.text
    return dhdl_options
             
    
## @brief Creates a EmGroup from a XML description
# @param model EditorialModel : the model which will contain the new group
# @param elem Element : the element which represents the EmGroup
# @return EmGroup
def load_group_xml(model, elem):
    uid = elem.find('uid')
    
    if elem.find('display_name').text is None:
        name = None
    else:
        name = load_mlstring_xml(elem.find('display_name'))
        
    if elem.find('help_text').text is None:
        help_text = None
    else:
        help_text = load_mlstring_xml(elem.find('help_text'))
        
    requires = list()
    groups = model.all_groups()
    req = elem.find('requires')

    if req.text is not None:
        l_req = req.text.split(',')
        for r in l_req:
            if r in groups:
                requires.append(model.all_groups_ref(r))
            else:
                grp = model.new_group(r)
                requires.append(grp)
                
    comp= list()
    components = elem.find('components')
    fields = components.find('emfields')
    for field in fields:
        fld_uid = field.find('uid').text
        fld_class = field.find('class').text
        fld = model.all_classes_ref(fld_class).fields(fld_uid)
        comp.append(fld)
    classes = components.find('emclasses')
    for classe in classes:
        comp.append(model.all_classes_ref(classe.text))
        
    groups = model.all_groups()
    if uid.text in groups:
        group = model.all_groups_ref(uid.text)
        group.display_name = name
        group.help_text = help_text
        group.add_dependency(requires)
    else:
        group = EmGroup(uid.text, requires, name, help_text)

    group.add_components(comp)     
    return group

## @brief Constructs a MlString from a XML description
# @param elem Element : the element which represents the MlString
# @return MlString
def load_mlstring_xml(elem):
    mlstr = dict()
    for lang in elem:
        mlstr[lang.tag] = lang.text 
    return MlString(mlstr)




        
