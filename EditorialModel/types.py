#-*- coding: utf-8 -*-

from Database import sqlutils
import sqlalchemy as sql

import EditorialModel
from EditorialModel.components import EmComponent, EmComponentNotExistError
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField
from EditorialModel.classtypes import EmNature, EmClassType
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
    table = 'em_type'
    table_hierarchy = 'em_type_hierarchy'
    ranked_in = 'class_id'

    ## @brief Specific EmClass fields
    # @see EditorialModel::components::EmComponent::_fields
    _fields = [
        ('class_id', ftypes.EmField_integer),
        ('icon', ftypes.EmField_icon),
        ('sortcolumn', ftypes.EmField_char)
        ]

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
    def create(c, name, em_class, sortcolumn='rank', icon=None, **em_component_args):
        return super(EmType, c).create(name=name, class_id=em_class.uid, sortcolumn=sortcolumn, **em_component_args)

    @property
    ## Return an sqlalchemy table for type hierarchy
    # @return sqlalchemy em_type_hierarchy table object
    # @todo Don't hardcode table name
    def _table_hierarchy(self):
        return sql.Table(self.__class__.table_hierarchy, sqlutils.meta(self.db_engine))

    @property
    ## Return the EmClassType of the type
    # @return EditorialModel.classtypes.*
    def classtype(self):
        return getattr(EmClassType, EditorialModel.classes.EmClass(self.class_id).classtype)

    ## @brief Delete an EmType
    # The deletion is only possible if a type is not linked by any EmClass
    # and if it has no subordinates
    # @return True if delete False if not deleted
    # @todo Check if the type is not linked by any EmClass
    # @todo Check if there is no other ''non-deletion'' conditions
    def delete(self):
        subs = self.subordinates()
        if sum([len(subs[subnat]) for subnat in subs]) > 0:
            return False
        #Delete all relation with superiors
        for nature,sups in self.superiors().items():
            for sup in sups:
                self.del_superior(sup, nature)
        return super(EmType, self).delete()
        

    ## Get the list of associated fieldgroups
    # @return A list of EmFieldGroup instance
    def field_groups(self):
        meta = sqlutils.meta(self.db_engine)
        fg_table = sql.Table(EmFieldGroup.table, meta)
        req = fg_table.select(fg_table.c.uid).where(fg_table.c.class_id == self.class_id)
        conn = self.db_engine.connect()
        res = conn.execute(req)
        rows = res.fetchall()
        conn.close()

        return [ EmFieldGroup(row['uid']) for row in rows ]

    ## Get the list of all Emfield possibly associated with this type
    # @return A list of EmField instance
    def all_fields(self):
        res = []
        for fieldgroup in self.field_groups():
            res += fieldgroup.fields()
        return res

    ## Return selected optional field
    # @return A list of EmField instance
    def selected_fields(self):
        dbe = self.db_engine
        meta = sqlutils.meta(dbe)
        conn = dbe.connect()

        table = sql.Table('em_field_type', meta)
        res = conn.execute(table.select().where(table.c.type_id == self.uid))

        return [ EditorialModel.fields.EmField(row['field_id']) for row in res.fetchall()]
    
    ## Return the list of associated fields
    # @return A list of EmField instance
    def fields(self):
        result = list()
        for field in self.all_fields():
            if not field.optional:
                result.append(field)
        return result+selected_fields

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
    def _opt_field_act(self, field, select=True):
        if not isinstance(field, EmField):
            raise TypeError("Excepted <class EmField> as field argument. But got "+str(type(field)))
        if not field in self.all_fields():
            raise ValueError("This field is not part of this type")
        if not field.optional:
            raise ValueError("This field is not optional")

        dbe = self.db_engine
        meta = sqlutils.meta(dbe)
        conn = dbe.connect()

        table = sql.Table('em_field_type', meta)
        if select:
            req = table.insert({'type_id': self.uid, 'field_id': field.uid})
        else:
            req = table.delete().where(table.c.type_id == self.uid and table.c.field_id == field.uid)

        res = conn.execute(req)
        conn.close()
        return bool(res)

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
    def del_hook(self,hook):
        raise NotImplementedError()

    
    ## @brief Get the list of subordinates EmType
    # Get a list of EmType instance that have this EmType for superior
    # @return Return a dict with relation nature as keys and values as a list of subordinates
    # EmType instance
    # @throw RuntimeError if a nature fetched from db is not valid
    def subordinates(self):
        return self._subOrSup(False)

    ## @brief Get the list of subordinates EmType
    # Get a list of EmType instance that have this EmType for superior
    # @return Return a dict with relation nature as keys and values as a list of subordinates
    # EmType instance
    # @throw RuntimeError if a nature fetched from db is not valid
    # @see EmType::_subOrSup()
    def superiors(self):
        return self._subOrSup(True)

    ## @brief Return the list of subordinates or superiors for an EmType
    # This is the logic function that implements EmType::subordinates() and EmType::superiors()
    # @param sup bool: If True returns superiors, if False returns..... subordinates
    # @return A dict with relation nature as keys and list of subordinates/superiors as values
    # @throw RunTimeError if a nature fetched from db is not valid
    # @see EmType::subordinates(), EmType::superiors()
    def _subOrSup(self, sup = True):
        conn = self.db_engine.connect()
        htable = self._table_hierarchy
        type_table = sqlutils.get_table(self)

        req = htable.select()
        if sup:
            col = htable.c.subordinate_id
        else:
            col = htable.c.superior_id

        req = req.where(col == self.uid)
        res = conn.execute(req)
        rows = res.fetchall()
        conn.close()

        result = dict()
        for nature in EmClassType.natures(self.classtype['name']):
            result[nature] = []

        for row in rows:
            if row['nature'] not in result:
                #Maybe security issue ?
                logger.error("Unreconized or unauthorized nature in Database for EmType<"+str(self.uid)+"> subordinate <"+str(row['subordinate_id'])+"> : '"+row['nature']+"'")
                raise RuntimeError("Unreconized nature from database : "+row['nature'])
            
            to_fetch = 'superior_id' if sup else 'subordinate_id'
            result[row['nature']].append( EmType(row[to_fetch]) )
        return result


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
            raise TypeError("Excepted <class EmType> and <class str> as em_type argument. But got : "+str(type(em_type))+" "+str(type(relation_nature)))
        if relation_nature not in EmClassType.natures(self.classtype['name']):
            raise ValueError("Invalid nature for add_superior : '"+relation_nature+"'. Allowed relations for this type are "+str(EmClassType.natures(self.classtype['name'])))

        #Checking that this relation is allowed by the nature of the relation
        att = self.classtype['hierarchy'][relation_nature]['attach']
        if att == 'classtype':
            if self.classtype['name'] != em_type.classtype['name']:
                raise ValueError("Not allowed to put an em_type with a different classtype as superior")
        elif self.name != em_type.name:
            raise ValueError("Not allowed to put a different em_type as superior in a relation of nature '"+relation_nature+"'")

        conn = self.db_engine.connect()
        htable = self._table_hierarchy
        values = { 'subordinate_id': self.uid, 'superior_id': em_type.uid, 'nature': relation_nature }
        req = htable.insert(values=values)

        try:
            res = conn.execute(req)
        except sql.exc.IntegrityError:
            ret = False
        else:
            ret = True
        finally:
            conn.close()

        return ret

    ## Delete a superior in the type hierarchy
    # @param em_type EmType: An EmType instance
    # @throw TypeError when em_type isn't an EmType instance
    def del_superior(self, em_type, relation_nature):
        if not isinstance(em_type, EmType):
            raise TypeError("Excepted <class EmType> as argument. But got : "+str(type(em_type)))
        if relation_nature not in EmClassType.natures(self.classtype['name']):
            raise ValueError("Invalid nature for add_superior : '"+relation_nature+"'. Allowed relations for this type are "+str(EmClassType.natures(self.classtype['name'])))

        conn = self.db_engine.connect()
        htable = self._table_hierarchy
        req = htable.delete(htable.c.superior_id == em_type.uid and htable.c.nature == relation_nature)
        conn.execute(req)
        conn.close()

    ## @brief Get the list of linked type
    # Types are linked with special fields called relation_to_type fields
    # @return a list of EmType
    # @see EmFields
    def linked_types(self):
        return self._linked_types_Db()

    ## @brief Return the list of all the types linked to this type, should they be superiors or subordinates
    # @return A list of EmType objects
    def _linked_types_Db(self):
        conn = self.db_engine.connect()
        htable = self._table_hierarchy
        req = htable.select(htable.c.superior_id, htable.c.subordinate_id)
        req = req.where(sql.or_(htable.c.subordinate_id == self.uid, htable.c.superior_id == self.uid))

        res = conn.execute(req)
        rows = res.fetchall()
        conn.close()

        rows = dict(zip(rows.keys(), rows))
        result = []
        for row in rows:
            result.append(EmType(row['subordinate_id'] if row['superior_id']==self.uid else row['superior_id']))

        return result
