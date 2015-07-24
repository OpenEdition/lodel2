# -*- coding: utf-8 -*-

## @file classes.py
# @see EditorialModel::classes::EmClass

from EditorialModel.components import EmComponent
from EditorialModel.classtypes import EmClassType
import EditorialModel.fieldtypes as ftypes
import EditorialModel


## @brief Manipulate Classes of the Editorial Model
# Create classes of object.
# @see EmClass, EmType, EditorialModel.fieldgroups.EmFieldGroup, EmField
# @todo sortcolumn handling
class EmClass(EmComponent):

    ranked_in = 'classtype'

    ## @brief Specific EmClass fields
    # @see EditorialModel::components::EmComponent::_fields
    _fields = [
        ('classtype', ftypes.EmField_char),
        ('icon', ftypes.EmField_icon),
        ('sortcolumn', ftypes.EmField_char)
    ]

    ## EmClass instanciation
    # @todo Classtype initialisation and test is not good EmClassType should give an answer or something like that
    # @todo defines types check for icon and sortcolumn
    def __init__(self, model, uid, name, classtype, icon = '0', sortcolumn = 'rank', string = None, help_text = None, date_update = None, date_create = None, rank = None):
        
        try:
            getattr(EmClassType, classtype)
        except AttributeError:
            raise AttributeError("Unknown classtype '%s'" %classtype)

        self.classtype = classtype
        self.icon = icon
        self.sortcolumn = 'rank'
        super(EmClass, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)
        pass
    

    ## Check if the EmComponent is valid
    # @return True if valid False if not
    def check(self):
        super(EmClass, self).check()
        return True

    ## @brief Delete a class if it's ''empty''
    # If a class has no fieldgroups delete it
    # @return bool : True if deleted False if deletion aborded
    def delete(self):
        for emtype in self.model.components(EmType):
            if emtype.class_id == self.uid:
                return False
        for fieldgroup in self.model.components(EditorialModel.fieldgroups.EmFieldGroup):
            if fieldgroup.class_id == self.uid:
                return False

        if self.model.delete_component(self.uid):
            return self.check()
        else:
            return False

    ## Retrieve list of the field_groups of this class
    # @return A list of fieldgroups instance
    def fieldgroups(self):
        ret = []
        for fieldgroup in self.model.components(EditorialModel.fieldgroups.EmFieldGroup):
            if fieldgroup.class_id == self.uid:
                ret.append(fieldgroup)
        return ret

    ## Retrieve list of fields
    # @return fields [EmField]:
    def fields(self):
        fieldgroups = self.fieldgroups()
        fields = []
        for fieldgroup in fieldgroups:
            fields += fieldgroup.fields()
        return fields

    ## Retrieve list of type of this class
    # @return types [EmType]:
    def types(self):
        ret = []
        for emtype in self.components(EmType):
            if emtype.class_id == self.uid:
                ret.append(emtype)
        return ret

    ## Add a new EmType that can ben linked to this class
    # @param  em_type EmType: type to link
    # @return success bool: done or not
    def link_type(self, em_type):
        pass

    ## Retrieve list of EmType that are linked to this class
    #  @return types [EmType]:
    def linked_types(self):
        pass

