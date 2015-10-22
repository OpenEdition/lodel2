# -*- coding: utf-8 -*-

## @package EditorialModel.backend.lodel1_backend
# @brief Handle convertion of lodel 1.0 model.xml
#

import xml.etree.ElementTree as ET
import datetime
import re
from Lodel.utils.mlstring import MlString
from EditorialModel.backend.dummy_backend import EmBackendDummy


## Manages a Json file based backend structure
class EmBackendLodel1(EmBackendDummy):
    def __init__(self, xml_file=None, xml_string=None):
        if (not xml_file and not xml_string) or (xml_file and xml_string):
            raise AttributeError
        self._xml_file = xml_file
        self._xml_string = xml_string
        self.lodel2_components = self._components = {'uids': {}, 'EmClass': [], 'EmType': [], 'EmField': [], 'EmFieldGroup': []}
        self._uids = []
        self._fieldgroups_map = {}

    ## Loads the data from given file or string
    #
    # @return list
    def load(self):
        xml_string = self._load_from_file() if self._xml_file else self._xml_string

        root_element = ET.fromstring(xml_string)
        self._import_components(root_element)

        # change uid of EmField and EmFieldGroup DONE
        # take care of fieldgroup_id 0 !!

        # add relational fields and rel_to_type_id

        # add superiors_list in types

        # create dict with all components DONE

        #print (self.lodel2_components)
        return self.lodel2_components['uids']

    ## Import the four basic components
    def _import_components(self, root_element):
        # component name and xpath to find them in the xml model
        # the order is very important
        # class and type first, they put their uid in self._uids
        # fieldgroups must change their uid, it will be used by fields later
        to_import = [
            ('EmClass', "./table[@name='#_TP_classes']/datas/row"),
            ('EmType', "./table[@name='##_TP_types']/datas/row"),
            ('EmFieldGroup', "./table[@name='#_TP_tablefieldgroups']/datas/row"),
            ('EmField', "./table[@name='#_TP_tablefields']/datas/row")
        ]
        for comp in to_import:
            component_name, xpath = comp
            #print (component_name, xpath)
            components = root_element.findall(xpath)
            for lodel1_component in components:
                cols = lodel1_component.findall('*')
                fields = self._dom_elements_to_dict(cols)
                #print(fields)
                lodel2_component = self._map_component(component_name, fields)
                lodel2_component['component'] = component_name
                #print(lodel2_component)
                uid = lodel2_component['uid']
                self.lodel2_components[component_name].append(lodel2_component)
                #if component_name in ['EmClass', 'EmType']:
                self._uids.append(uid)
                #del lodel2_component['uid']
                self.lodel2_components['uids'][uid] = lodel2_component
                #print ('————')

    def _get_uid(self):
        uid = 1
        while True:
            if uid not in self._uids:
                return uid
            uid += 1

    ## map lodel1 values to lodel2 values
    def _map_component(self, component, fields):
        new_dic = {}
        for mapping in ONE_TO_TWO[component]:
            lodel1_fieldname, lodel2_fieldname = mapping[0:2]
            if len(mapping) == 3:
                cast_function = mapping[2]
                if callable(cast_function):
                    value = cast_function(fields[lodel1_fieldname])
                    values = {lodel2_fieldname: value}
                else:
                    values = getattr(self, cast_function)(lodel2_fieldname, fields[lodel1_fieldname], fields)
            else:
                values = {lodel2_fieldname: fields[lodel1_fieldname]}
            if values:
                for name, value in values.items():
                    new_dic[name] = value
            #print (lodel1_fieldname, lodel2_fieldname, value)
        return new_dic

    ## convert collection of dom element to a dict
    # \<col name="id"\>252\</col\> => {'id':'252'}
    def _dom_elements_to_dict(self, elements):
        fields = {}
        for element in elements:
            if 'name' in element.attrib:
                fields[element.attrib['name']] = element.text if element.text is not None else ''
        return fields

    def _load_from_file(self):
        with open(self._xml_file) as content:
            data = content.read()
        return data

    def save(self, model, filename=None):
        pass

    # Map methods lodel1 to lodel2

    ## combine title and altertitle into one MlString
    def title_to_mlstring(self, name, value, fields):
        title = MlString({'fre': value})
        if 'altertitle' in fields:
            langs = re.findall('lang="(..)">([^<]*)', fields['altertitle'])
            for string in langs:
                title.set(string[0], string[1])
        return {name: title}

    ## set a new unused uid for EmFieldGroup
    # save the oldid to apply to fields
    def new_fieldgroup_id(self, name, value, fields):
        uid = self._get_uid()
        print(value)
        self._fieldgroups_map[int(value)] = uid
        return {name: uid}

    # give a new unused uid
    def new_uid(self, name, value, fields):
        uid = self._get_uid()
        return {name: uid}

    # return the new fieldgroup_id given the old one
    def fieldgroup_id(self, name, value, fields):
        old_id = int(value)
        try:
            new_id = self._fieldgroups_map[old_id]
        except KeyError:
            print(old_id, fields)
            return False
        return {name: new_id}

    def mlstring_cast(self, name, value, fields):
        return {name: MlString({'fre': value})}

    def to_classid(self, name, value, fields):
        for em_class in self.lodel2_components['EmClass']:
            if em_class['name'] == value:
                return {name: em_class['uid']}
        return False

    def date_cast(self, name, value, fields):
        date = None
        if len(value):
            try:  # 2015-09-14 14:20:28
                date = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
        return {name: date}

    def classtype_cast(self, name, value, fields):
        classtype_map = {'entries': 'entry', 'entities': 'entity', 'persons': 'person'}
        if value in classtype_map:
            return {name: classtype_map[value]}
        return False

    def map_fieldtypes(self, name, value, fields):
        fieldtypes = {
            'longtext': 'text',
            'date': 'datetime',
            'tinytext': 'text',
            'lang': 'char',
            'boolean': 'bool',
            'email': 'char',
            'url': 'char',
            'mltext': 'text',
            'image': 'text',
            'number': 'int',
            #'persons': 'rel2type',
            #'entries': 'rel2type',
            #'entities': 'rel2type',
            'persons': 'text',
            'entries': 'text',
            'entities': 'text'
        }
        if value in fieldtypes:
            return {name: fieldtypes[value]}
        return {name: value}


ONE_TO_TWO = {
    'EmClass': [
        ("id", "uid", int),
        ("icon", "icon"),
        ("class", "name"),
        ("title", "string", 'title_to_mlstring'),
        ("classtype", "classtype", 'classtype_cast'),
        ("comment", "help_text", 'mlstring_cast'),
        #("status",""),
        ("rank", "rank", int),
        ("upd", "date_update", 'date_cast')
    ],
    'EmFieldGroup': [
        ("id", "uid", 'new_fieldgroup_id'),
        ("name", "name"),
        ("class", "class_id", 'to_classid'),
        ("title", "string", 'title_to_mlstring'),
        ("comment", "help_text", 'mlstring_cast'),
        #("status",""),
        ("rank", "rank", int),
        ("upd", "date_update", 'date_cast')
    ],
    'EmType': [
        ("id", "uid", int),
        ("icon", "icon"),
        ("type", "name"),
        ("title", "string", 'title_to_mlstring'),
        ("class", "class_id", 'to_classid'),
        ("comment", "help_text", 'mlstring_cast'),
        #("status",""),
        ("rank", "rank", int),
        ("upd", "date_update", 'date_cast')
    ],
    'EmField': [
        ("id", "uid", 'new_uid'),
        ("name", "name"),
        ("idgroup", "fieldgroup_id", 'fieldgroup_id'),
        ("type", "fieldtype", 'map_fieldtypes'),
        ("title", "string", 'title_to_mlstring'),
        ("comment", "help_text", 'mlstring_cast'),
        #("status",""),
        ("rank", "rank", int),
        ("upd", "date_update", 'date_cast')
    ]
}
