# -*- coding: utf-8 -*-

## @file classes.py
# @see EditorialModel::classes::EmClass

import copy

import EditorialModel
from EditorialModel.components import EmComponent
from EditorialModel.classtypes import EmClassType


## @brief Manipulate Classes of the Editorial Model
# Create classes of object.
# @see EmClass, EditorialModel.types.EmType, EditorialModel.fieldgroups.EmFieldGroup, EmField
# @todo sortcolumn handling
class EmClass(EmComponent):

    ranked_in = 'classtype'

    ## EmClass instanciation
    # @todo Classtype initialisation and test is not good EmClassType should give an answer or something like that
    # @todo defines types check for icon and sortcolumn
    def __init__(self, model, uid, name, classtype, icon='0', sortcolumn='rank', string=None, help_text=None, date_update=None, date_create=None, rank=None):

        if EmClassType.get(classtype) is None:
            raise AttributeError("Unknown classtype '%s'" % classtype)

        self.classtype = classtype
        self.icon = icon
        self.sortcolumn = sortcolumn  # 'rank'
        super(EmClass, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)

    ## Check if the EmComponent is valid
    # @note this function add default and common fields to the EmClass if they are not yet created
    # @throw EmComponentCheckError if fails
    def check(self):
        for fname in self.default_fields_list().keys():
            if fname not in [f.name for f in self.fields()]:
                self.model.add_default_class_fields(self.uid)
        super(EmClass, self).check()

    ## @brief Return the default fields list for this EmClass
    # @return a dict with key = fieldname and value is a dict to pass to the EditorialModel::model::Model::creat_component() method
    def default_fields_list(self):
        ctype = EditorialModel.classtypes.EmClassType.get(self.classtype)
        res = ctype['default_fields']
        for k, v in EditorialModel.classtypes.common_fields.items():
            res[k] = copy.copy(v)
        return res

    ## @brief Delete a class if it's ''empty''
    # If a class has no fieldgroups delete it
    # @return bool : True if deleted False if deletion aborded
    def delete_check(self):
        for emtype in self.model.components(EditorialModel.types.EmType):
            if emtype.class_id == self.uid:
                return False
        #If the class contains EmField that are not added by default, you cannot delete the EmClass
        if len([f for f in self.fields() if f.name not in self.default_fields_list().keys()]) > 0:
            return False
        return True

    ## Retrieve list of the field_groups of this class
    # @return A list of fieldgroups instance
    def _fieldgroups(self):
        ret = []
        for fieldgroup in self.model.components(EditorialModel.fieldgroups.EmFieldGroup):
            if fieldgroup.class_id == self.uid:
                ret.append(fieldgroup)
        return ret

    ## Retrieve list of fields
    # @return fields [EmField]:
    def fields(self, relational=True):
        if relational:
            return [f for f in self.model.components('EmField') if f.class_id == self.uid]
        else:
            return [f for f in self.model.components('EmField') if f.class_id == self.uid and f.fieldtype != 'rel2type' and f.rel_field_id is None]

    ## Retrieve list of type of this class
    # @return types [EditorialModel.types.EmType]:
    def types(self):
        ret = []
        for emtype in self.model.components(EditorialModel.types.EmType):
            if emtype.class_id == self.uid:
                ret.append(emtype)
        return ret

    ## Add a new EditorialModel.types.EmType that can ben linked to this class
    # @param  em_type EditorialModel.types.EmType: type to link
    # @return success bool: done or not
    # @deprecated To do this add a rel2type field to any fieldtype of this EmClass
    def link_type(self, em_type):
        pass

    ## Retrieve list of EditorialModel.types.EmType that are linked to this class
    #  @return types [EditorialModel.types.EmType]:
    def linked_types(self):
        res = list()
        for field in self.fields():
            if field.fieldtype_instance().name == 'rel2type':
                res.append(self.model.component(field.rel_to_type_id))
        return res
