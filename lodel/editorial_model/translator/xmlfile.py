#-*- coding: utf-8 -*-

import lxml
import os
from lxml import etree
from lodel.editorial_model.model import EditorialModel
from lodel.editorial_model.components import *
from lodel.utils.mlstring import MlString

##@brief Saves a model in a xml file
# @param model EditorialModel : the model to save
# @param filename str|None : if None display on stdout else writes in the file filename
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
                          classes[emclass].fields(), classes[emclass].parents, 
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
    
    
##@brief Writes a representation of a MlString in xml
# @param etree : the xml object
# @param elem : the element which represents a MlString
# @param mlstr : the mlstr to write
def write_mlstring_xml(etree, elem, mlstr):
    for lang in mlstr.values:
        ss_mlstr = etree.SubElement(elem,lang)
        ss_mlstr.text = mlstr.get(lang)
        
##@brief Writes the definition of a datahandler in xml
# @param etree : the xml object
# @param elem : the element which defines a datahandler
# @param dhdl_name : the name of the datahandler
# @param kwargs : the options of the datahandler
def write_datahandler_xml(etree, elem, dhdl_name, **kwargs):
    dhdl = etree.SubElement(elem,'datahandler_name')
    dhdl.text = dhdl_name
    dhdl_opt = etree.SubElement(elem, 'datahandler_options')
    for argname, argval in kwargs.items():
        arg = etree.SubElement(dhdl_opt, argname)
        arg.text = argval
        
##@brief Writes a representation in xml of a EmField
# @param etree : the xml object
# @param elem : the element for the EmField
# @param uid : the uid of the EmField
# @param name : the name of the field
# @param help_text : explanations of the EmField
# @param group_uid : the uid of a group, can be None
# @datahandler_name
# @**kwargs : options of the datahandler
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
# @param elem : the element for the EmGroup
# @param name  : the name of the group
# @param help_text : explanations of the EmGroup
# @param requires : a list of the group's uids whose this group depends
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
            #write_emfield_xml(etree, emgroup_comp_fld, component.uid, component.display_name, 
            #                   component.help_text, component.group, component.data_handler_name, **(component.data_handler_options))
        elif isinstance(component, EmClass):
            em_group_comp_cls_ins = etree.SubElement(emgroup_comp_cls, 'emclass')
            em_group_comp_cls_ins.text = component.uid
            #write_emclass_xml(etree, emgroup_comp_cls, component.uid, component.display_name, component.help_text, component.group, 
            #                  component.fields(), component.parents, component.abstract, component.pure_abstract)

##@brief Writes a representation of a EmClass in xml
# @param etree : the xml object
# @param elem : the element for the EmClass
# @param name  : the name of the group
# @param help_text : explanations of the EmClass
# @param fields : a dict
# @param parents : a list of EmClass uids
# @param abstract : a boolean
# @param pure_abstract : a boolean
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
        emclass_group.text = group.uid #write_emgroup_xml(etree, emclass_group, group.uid, group.name, group.help_text, group.require, group.components)
    emclass_fields = etree.SubElement(emclass, 'fields')
    for field in fields:
        write_emfield_xml(etree, emclass_fields, field.uid, field.display_name, field.help_text, 
                          field.group,field.data_handler_name, **field.data_handler_options)
    parents_list=list()
    for parent in parents:
        parents_list.append(parent['uid'])
    emclass_parents = etree.SubElement(emclass, 'parents')
    emclass_parents.text = ",".join(parents_list)

##@brief Loads a model from a xml file
# @param model EditorialModel : the model to load
# @return a new EditorialModel object
def load(**kwargs):

    Em = etree.parse(kwargs['filename'])
    emodel = Em.getroot()
    name = emodel.find('name')
    description = emodel.find('description')

    model = EditorialModel(load_mlstring_xml(name), load_mlstring_xml(description))
        
    classes = emodel.find('classes')
    for emclass in classes:
        model.add_class(load_class_xml(model, emclass))
    
    groups = emodel.find('groups')
    for group in groups:
        grp = load_group_xml(model, group)
        if grp.uid not in model.all_groups():
            grp = model.add_group(grp)

    return model

##@brief Creates a EmClass from a xml description
# @param elem : the element which represents the EmClass
# @param model  : the model which will contain the new class
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
        
    abstract = True if elem.find('abstract').text == 'True' else False
    pure_abstract = True if elem.find('pure_abstract').text == 'True' else False
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
    if group:
        grp = model.add_group(EmGroup(group.text))
    else:
        grp = None
        
    if uid in classes:
        emclass = model.all_classes_ref(uid)
        emclass.display_name = name
        emclass.help_text = help_text
        emclass.parents=requires
        emclass.group = grp
    else:
        emclass = EmClass(uid, name, help_text, abstract,requires, grp, pure_abstract)
        
    fields = elem.find('fields')
    for field in fields:
        emfield = load_field_xml(model, field)
        l_emfields = emclass.fields()
        incls = False
        for emf in l_emfields:
            if emfield.uid == emf.uid:
                incls = True
        if not incls:
            emclass.add_field(emfield)
            
    return emclass
    
##@brief Creates a EmField from a xml description
# @param elem : the element which represents the EmField
# @param model  : the model which will contain the new field
# @return a new EmField object
def load_field_xml(model, elem):
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
    if emgroup:
        group = model.add_group(EmGroup(emgroup.text))
    else:
        group = None
    dhdl = elem.find('datahandler_name')
    if elem.find('datahandler_options').text is not None:
        dhdl_options = elem.find('datahandler_options').text.split()
        emfield = EmField(uid, dhdl, name, help_text, group, **dhdl_options)
    else:
        emfield = EmField(uid, dhdl.text, name, help_text, group)
    
    return emfield

##@brief Creates a EmGroup from a xml description
# @param elem : the element which represents the EmGroup
# @param model  : the model which will contain the new group
# @return a new EmGroup object
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
                
    if uid in groups:
        group = model.all_groups_ref(uid)
        group.display_name = name
        group.help_text = help_text
        group.add_dependencie(requires)
    else:
        group = EmGroup(uid.text, requires, name, help_text)
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
    group.add_components(comp)
        
    return group

##@brief Constructs a MlString from a xml description
# @param elem : the element which represents the MlString
# @param model  : the model which will contain the new group
# @return a new MlString object
def load_mlstring_xml(elem):
    mlstr = dict()
    for lang in elem:
        mlstr[lang.tag] = lang.text 
    return MlString(mlstr)




        