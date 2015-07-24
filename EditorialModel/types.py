#-*- coding: utf-8 -*-

# from Database import sqlutils
# import sqlalchemy as sql

import EditorialModel
from EditorialModel.components import EmComponent
from EditorialModel.fields import EmField
from EditorialModel.classtypes import EmClassType
from EditorialModel.exceptions import *
import EditorialModel.fieldtypes as ftypes
import EditorialModel.classes


## Represents type of documents
# A type is a specialisation of a class, it can select optional field,
# they have hooks, are organized in hierarchy and linked to other
# EmType with special fields called relation_to_type fields
#
# @see EditorialModel::components::EmComponent
# @todo sortcolumn handling
class EmType(EmComponent):
    ranked_in = 'class_id'

    ## Instanciate a new EmType
    # @todo define and check types for icon and sortcolumn
    # @todo better check self.subordinates
    def __init__(self, model, uid, name, class_id, fields_list = [], subordinates_list = {}, icon = '0', sortcolumn = 'rank', string = None, help_text = None, date_update = None, date_create = None, rank = None):
        self.class_id = class_id
        self.check_type('class_id', int)
        self.fields_list = fields_list
        self.check_type('fields_list', list)
        for l_uid in self.fields_list:
            if not isinstance(l_uid, int):
                raise AttributeError("Excepted fields_list to be a list of integers, but found a +"+str(type(l_uid))+" in it")

        self.subordinates_list = subordinates_list
        print(subordinates_list)
        self.check_type('subordinates_list', dict)
        for nature, uids in self.subordinates_list.items():
            for uid in uids:
                if not isinstance(uid, int):
                    raise AttributeError("Excepted subordinates of nature %s to be a list int !" % nature)

        self.icon = icon
        self.sortcolumn = sortcolumn
        super(EmType, self).__init__(model=model, uid=uid, name=name, string=string, help_text=help_text, date_update=date_update, date_create=date_create, rank=rank)
        pass

    @classmethod
    ## Create a new EmType and instanciate it
    # @param name str: The name of the new type
    # @param em_class EmClass: The class that the new type will specialize
    # @param **em_component_args : @ref EditorialModel::components::create()
    # @return An EmType instance
    # @throw EmComponentExistError if an EmType with this name but different attributes exists
    # @see EmComponent::__init__()
    #
    # @todo check that em_class is an EmClass object (fieldtypes can handle it)
    def create(cls, name, em_class, sortcolumn='rank', **em_component_args):
        return super(EmType, cls).create(name=name, class_id=em_class.uid, sortcolumn=sortcolumn, **em_component_args)

    @property
    ## Return the EmClassType of the type
    # @return EditorialModel.classtypes.*
    def classtype(self):
        return getattr(EmClassType, self.em_class.classtype)

    @property
    ## Return an instance of the class this type belongs to
    # @return EditorialModel.EmClass
    def em_class(self):
        return self.model.component(self.class_id)

    ## @brief Delete an EmType
    # The deletion is only possible if a type is not linked by any EmClass
    # and if it has no subordinates
    # @return True if delete False if not deleted
    # @todo Check if the type is not linked by any EmClass
    # @todo Check if there is no other ''non-deletion'' conditions
    def delete(self):
        if sum(self.subordinates_list) > 0:
            return False
        #Delete all relation with superiors
        for nature, sups in self.superiors().items():
            for sup in sups:
                self.del_superior(sup, nature)
        if super(EmType, self).delete():
            return self.check()
        else:
            return False

    ## Get the list of non empty associated fieldgroups
    # @return A list of EmFieldGroup instance
    def fieldgroups(self):
        fieldgroups = [fieldgroup for fieldgroup in self.em_class.fieldgroups() if len(fieldgroup.fields(self.uid))]
        return fieldgroups

    ## Return selected optional field
    # @return A list of EmField instance
    def selected_fields(self):
        selected = [self.model.component(field_id) for field_id in self.fields_list]
        return selected

    ## Return the list of associated fields
    # @return A list of EmField instance
    def fields(self):
        fields = [field for fieldgroup in self.fieldgroups() for field in fieldgroup.fields(self.uid)]
        return fields

    ## Select_field (Function)
    #
    # Indicates that an optional field is used
    #
    # @param field EmField: The optional field to select
    # @return True if success False if failed
    #
    # @throw TypeError if field is not an EmField instance
    # @throw ValueError if field is not optional or is not associated with this type
    # @see EmType::_opt_field_act()
    def select_field(self, field):
        return self._opt_field_act(field, True)

    ## Unselect_field (Function)
    #
    # Indicates that an optional field will not be used
    #
    # @param field EmField: The optional field to unselect
    # @return True if success False if fails
    #
    # @throw TypeError if field is not an EmField instance
    # @throw ValueError if field is not optional or is not associated with this type
    # @see EmType::_opt_field_act()
    def unselect_field(self, field):
        return self._opt_field_act(field, False)

    ## @brief Select or unselect an optional field
    # @param field EmField: The EmField to select or unselect
    # @param select bool: If True select field, else unselect it
    # @return True if success False if fails
    #
    # @throw TypeError if field is not an EmField instance
    # @throw ValueError if field is not optional or is not associated with this type
    def _opt_field_act(self, field, select=True):  # TODO voir si on conserve l'argument "select"
        if not isinstance(field, EmField):
            raise TypeError("Excepted <class EmField> as field argument. But got " + str(type(field)))
        if not field in self.all_fields():
            raise ValueError("This field is not part of this type")
        if not field.optional:
            raise ValueError("This field is not optional")

        # TODO Réimplémenter

        # dbe = self.db_engine
        # meta = sqlutils.meta(dbe)
        # conn = dbe.connect()
        #
        # table = sql.Table('em_field_type', meta)
        # if select:
        #     req = table.insert({'type_id': self.uid, 'field_id': field.uid})
        # else:
        #     req = table.delete().where(table.c.type_id == self.uid and table.c.field_id == field.uid)
        #
        # res = conn.execute(req)
        # conn.close()
        # return bool(res)

    ## Get the list of associated hooks
    # @note Not conceptualized yet
    # @todo Conception
    def hooks(self):
        raise NotImplementedError()

    ## Add a new hook
    # @param hook EmHook: An EmHook instance
    # @throw TypeError
    # @note Not conceptualized yet
    # @todo Conception
    def add_hook(self, hook):
        raise NotImplementedError()

    ## Delete a hook
    # @param hook EmHook: An EmHook instance
    # @throw TypeError
    # @note Not conceptualized yet
    # @todo Conception
    # @todo Maybe we don't need a EmHook instance but just a hook identifier
    def del_hook(self, hook):
        raise NotImplementedError()

    ## @brief Get the list of subordinates EmType
    # Get a list of EmType instance that have this EmType for superior
    # @return Return a dict with relation nature as keys and values as a list of subordinates
    # EmType instance
    # @throw RuntimeError if a nature fetched from db is not valid
    def subordinates(self):
        return { nature: [ self.model.component(tuid) for tuid in self.subordinates_list[nature] ] for nature in self.subordinates_list }

    ## @brief Get the list of subordinates EmType
    # Get a list of EmType instance that have this EmType for superior
    # @return Return a dict with relation nature as keys and values as a list of subordinates
    # EmType instance
    # @throw RuntimeError if a nature fetched from db is not valid
    # @see EmType::_sub_or_sup()
    # @todo reimplementation needed
    def superiors(self):
        pass

    ## Add a superior in the type hierarchy
    # @param em_type EmType: An EmType instance
    # @param relation_nature str: The name of the relation's nature
    # @return False if no modification made, True if modifications success
    #
    # @throw TypeError when em_type not an EmType instance
    # @throw ValueError when relation_nature isn't reconized or not allowed for this type
    # @throw ValueError when relation_nature don't allow to link this types together
    def add_superior(self, em_type, relation_nature):
        if not isinstance(em_type, EmType) or not isinstance(relation_nature, str):
            raise TypeError("Excepted <class EmType> and <class str> as em_type argument. But got : " + str(type(em_type)) + " " + str(type(relation_nature)))
        if relation_nature not in EmClassType.natures(self.classtype['name']):
            raise ValueError("Invalid nature for add_superior : '" + relation_nature + "'. Allowed relations for this type are " + str(EmClassType.natures(self.classtype['name'])))

        #Checking that this relation is allowed by the nature of the relation
        att = self.classtype['hierarchy'][relation_nature]['attach']
        if att == 'classtype':
            if self.classtype['name'] != em_type.classtype['name']:
                raise ValueError("Not allowed to put an em_type with a different classtype as superior")
        elif self.name != em_type.name:
            raise ValueError("Not allowed to put a different em_type as superior in a relation of nature '" + relation_nature + "'")

        # TODO Réimplémenter
        # conn = self.db_engine.connect()
        # htable = self._table_hierarchy
        # values = {'subordinate_id': self.uid, 'superior_id': em_type.uid, 'nature': relation_nature}
        # req = htable.insert(values=values)
        #
        # try:
        #     conn.execute(req)
        # except sql.exc.IntegrityError:
        #     ret = False
        # else:
        #     ret = True
        # finally:
        #     conn.close()
        #
        # return ret

    ## Delete a superior in the type hierarchy
    # @param em_type EmType: An EmType instance
    # @throw TypeError when em_type isn't an EmType instance
    def del_superior(self, em_type, relation_nature):
        if not isinstance(em_type, EmType):
            raise TypeError("Excepted <class EmType> as argument. But got : " + str(type(em_type)))
        if relation_nature not in EmClassType.natures(self.classtype['name']):
            raise ValueError("Invalid nature for add_superior : '" + relation_nature + "'. Allowed relations for this type are " + str(EmClassType.natures(self.classtype['name'])))

        # TODO Réimplémenter
        # conn = self.db_engine.connect()
        # htable = self._table_hierarchy
        # req = htable.delete(htable.c.superior_id == em_type.uid and htable.c.nature == relation_nature)
        # conn.execute(req)
        # conn.close()

    ## @brief Get the list of linked type
    # Types are linked with special fields called relation_to_type fields
    # @return a list of EmType
    # @see EmFields
    def linked_types(self):
        return self._linked_types_db()  # TODO changer l'appel

    ## @brief Return the list of all the types linked to this type, should they be superiors or subordinates
    # @return A list of EmType objects
    # def _linked_types_db(self):
    #     conn = self.db_engine.connect()
    #     htable = self._table_hierarchy
    #     req = htable.select(htable.c.superior_id, htable.c.subordinate_id)
    #     req = req.where(sql.or_(htable.c.subordinate_id == self.uid, htable.c.superior_id == self.uid))
    #
    #     res = conn.execute(req)
    #     rows = res.fetchall()
    #     conn.close()
    #
    #     rows = dict(zip(rows.keys(), rows))
    #     result = []
    #     for row in rows:
    #         result.append(EmType(row['subordinate_id'] if row['superior_id'] == self.uid else row['superior_id']))
    #
    #     return result
    
    ## Checks if the EmType is valid
    # @throw EmComponentCheckError if check fails
    def check(self):
        super(EmType, self).check()
        em_class = self.model.component(self.class_id)
        if not em_class:
            raise EmComponentCheckError("class_id contains an uid that does not exists '%d'" % self.class_id)
        if not isinstance(em_class, EditorialModel.classes.EmClass):
            raise EmComponentCheckError("class_id contains an uid from a component that is not an EmClass but a %s" % str(type(emc_class)))
        
        for i,fuid in enumerate(self.fields_list):
            field = self.model.component(fuid)
            if not field:
                raise EmComponentCheckError("The element %d of selected_field is a non existing uid '%d'"%(i, fuid))
            if not isinstance(field, EmField):
                raise EmComponentCheckError("The element %d of selected_field is not an EmField but a %s" % (i, str(type(field)) ))
            if not field.optional:
                raise EmComponentCheckError("The element %d of selected_field is an EmField not optional"  % i )
            if field.fieldgroup_id not in [ fg.uid for fg in self.fieldgroups() ]:
                raise EmComponentCheckErrro("The element %d of selected_field is an EmField that is part of an EmFieldGroup that is not associated with this EmType" % i)
        for nature in self.subordinates_list:
            for i, tuid in enumerate(self.subordinates_list[nature]):
                em_type = self.model.component(tuid)
                if not em_type:
                    raise EmComponentCheckError("The element %d of subordinates contains a non existing uid '%d'" % (i, tuid))
                if not isinstance(em_type, EmType):
                    raise EmComponentCheckError("The element %d of subordinates contains a component that is not an EmType but a %s" % (i, str(type(em_type))))
                if nature not in EmClassType.natures(self.em_class.classtype):
                    raise EmComponentCheckError("The relation nature '%s' of the element %d of subordinates is not valid for this EmType classtype '%s'", (nature, i, self.classtype) )
    
                nat_spec = getattr(EmClassType, self.em_class.classtype)['hierarchy'][nature]
    
                if nat_spec['attach'] == 'classtype':
                    if self.classtype != em_type.classtype:
                        raise EmComponentCheckError("The element %d of subordinates is of '%s' classtype. But the current type is of '%s' classtype, and relation nature '%s' require two EmType of same classtype" % (i, em_type.classtype, self.classtype, nature) )
                elif nat_spec['attach'] == 'type':
                    if self.uid != em_type.uid:
                        raise EmComponentCheckError("The element %d of subordinates is a different EmType. But the relation nature '%s' require the same EmType" % (i, nature))
                else:
                    raise NotImplementedError("The nature['attach'] '%s' is not implemented in this check !" % nat_spec['attach'])
    
                if 'max_depth' in nat_spec and nat_spec['max_depth'] > 0:
                    depth = 1
                    cur_type = em_type
                    while depth >= nat_spec['max_depth']:
                        depth +=1
                        if len(cur_type.subordinates()[nature]) == 0:
                            break
                    else:
                        raise EmComponentCheckError("The relation with the element %d of subordinates has a depth superior than the maximum depth ( %d ) allowed by the relation's nature ( '%s' )" %( i, nat_spec['max_depth'], nature) )
        
        for nature in self.subordinates():
            nat_spec = getattr(EmClassType, self.em_class.classtype)['hierarchy'][nature]
            if 'max_child' in nat_spec and nat_spec['max_child'] > 0:
                if len(self.subordinates()[nature]) > nat_spec['max_child']:
                    raise EmComponentCheckError("The EmType has more child than allowed in the relation's nature : %d > %d" (len(self.subordinates()[nature], nat_spec['max_child'])))
        #pass

