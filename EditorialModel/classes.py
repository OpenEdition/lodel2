# -*- coding: utf-8 -*-

## @file classes.py
# @see EditorialModel::classes::EmClass

import copy

# imports used in classtypes <-> actual model checks
import difflib
import warnings

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

    ## @brief Check if the EmComponent is valid
    # 
    # This function add default and common fields to the EmClass if they are not yet created (and raises warning if existing common fields are outdated given the one describe in EditorialModel.classtypes
    # @throw EmComponentCheckError if fails
    # 
    # @warning If default parameters of EmField constructor changes this method can be broken
    def check(self):
        # Checks that this class is up to date given the common_fields described in EditorialModel.classtypes
        # if not just print a warning, don't raise an Exception
        for field in self.fields():
            if field.name in EditorialModel.classtypes.common_fields:
                # Building fieltypes options to match the ones stored in EditorialModel.classtypes
                ftype_opts = field.fieldtype_options()
                ftype_opts['fieldtype'] = field.fieldtype

                ctype_opts = EditorialModel.classtypes.common_fields[field.name]
                #Adding default value for options nullable, uniq and internal to fieldtypes options stored in classtypes
                defaults = { 'nullable': False, 'uniq': False, 'internal': False}
                for opt_name, opt_val in defaults.items():
                    if opt_name not in ctype_opts:
                        ctype_opts[opt_name] = opt_val

                if ftype_opts != ctype_opts:
                    field.set_fieldtype_options(**ctype_opts)
                    # If options mismatch produce a diff and display a warning
                    ctype_opts = [ "%s: %s\n"%(repr(k), repr(ctype_opts[k])) for k in sorted(ctype_opts.keys())]
                    ftype_opts = [ "%s: %s\n"%(repr(k), repr(ftype_opts[k])) for k in sorted(ftype_opts.keys())]

                    diff_list = difflib.unified_diff(
                        ctype_opts,
                        ftype_opts, 
                        fromfile="Classtypes.%s" % field.name,
                        tofile="CurrentModel_%s.%s" % (self.name, field.name)
                    )
                    diff = ''.join(diff_list)
                    warnings.warn("LOADED MODEL IS OUTDATED !!! The common_fields defined in classtypes differs from the fields in this model.\nHere is a diff : \n%s" % diff)
            
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
