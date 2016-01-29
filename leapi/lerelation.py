#-*- coding: utf-8 -*-

import copy
import re
import warnings

import EditorialModel.classtypes
import EditorialModel.fieldtypes.leo as ft_leo
from . import lecrud
from . import leobject
from . import lefactory

## @brief Main class for relations
class _LeRelation(lecrud._LeCrud):

    _superior_field_name = None
    _subordinate_field_name = None
    ## @brief Stores the list of fieldtypes that are common to all relations
    _rel_fieldtypes = dict()

    def __init__(self, id_relation, **kwargs):
        super().__init__(id_relation, **kwargs)
  
    ## @brief Forge a filter to match the superior
    @classmethod
    def sup_filter(self, leo):
        if isinstance(leo, leobject._LeObject):
            return (self._superior_field_name, '=', leo)

    ## @brief Forge a filter to match the superior
    @classmethod
    def sub_filter(self, leo):
        if isinstance(leo, leobject._LeObject):
            return (self._subordinate_field_name, '=', leo)

    
    ## @return The name of the uniq id field
    @classmethod
    def uidname(cls):
        return EditorialModel.classtypes.relation_uid

    ## @return a dict with field name as key and fieldtype instance as value
    @classmethod
    def fieldtypes(cls):
        rel_ft = dict()
        rel_ft.update(cls._uid_fieldtype)

        rel_ft.update(cls._rel_fieldtypes)
        return rel_ft

    @classmethod
    def _prepare_relational_fields(cls, field):
        return lecrud.LeApiQueryError("Relational field '%s' given but %s doesn't is not a LeObject" % (field,
                                                                                                        cls.__name__))
    ## @brief Prepare filters before sending them to the datasource
    # @param cls : Concerned class
    # @param filters_l list : List of filters
    # @return prepared and checked filters
    @classmethod
    def _prepare_filters(cls, filters_l):
        filters, rel_filters = super()._prepare_filters(filters_l)
        res_filters = list()
        for field, op, value in filters:
            if field in [cls._superior_field_name, cls._subordinate_field_name]:
                if isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError as e:
                        raise LeApiDataCheckError("Wrong value given for '%s'"%field)
                if isinstance(value, int):
                    value = cls.name2class('LeObject')(value)
            res_filters.append( (field, op, value) )
        return res_filters, rel_filters

    ## @brief move to the first rank
    # @return True in case of success, False in case of failure
    def move_first(self):
        return self.set_rank('first')

    ## @brief move to the last rank
    # @return True in case of success, False in case of failure
    def move_last(self):
        return self.set_rank('last')

    ## @brief move to the given rank defined by a shift step
    # @param step int : The step
    # @return True in case of success, False in case of failure
    # @throw ValueError if step is not castable into an integer
    def shift_rank(self, step):
        step = int(step)
        return self.set_rank(self.rank + step)
    
    ## @brief modify a relation rank
    # @param new_rank int|str : The new rank can be an integer > 1 or strings 'first' or 'last'
    # @return True in case of success, False in case of failure
    # @throw ValueError if step is not castable into an integer
    def set_rank(self, new_rank):
        raise NotImplemented("Abtract method")
    
    ## @brief Implements set_rank
    def _set_rank(self, new_rank, **get_max_rank_args):
        max_rank = self.get_max_rank(**get_max_rank_args)
        try:
            new_rank = int(new_rank)
        except ValueError:
            if new_rank == 'first':
                new_rank = 1
            elif new_rank == 'last':
                new_rank = max_rank
            else:
                raise ValueError("The new rank can be an integer > 1 or strings 'first' or 'last', but %s given"%new_rank)

        if self.rank == new_rank:
            return True

        if new_rank < 1:
            if strict:
                raise ValueError("Rank must be >= 1, but %d given"%rank)
            new_rank = 1
        elif new_rank > max_rank:
            if strict:
                raise ValueError("Rank is too big (max_rank = %d), but %d given"%(max_rank,rank))
            new_rank = max_rank
        self._datasource.update_rank(self, new_rank)
    
    ## @returns The maximum assignable rank for this relation
    # @todo implementation
    def get_max_rank(self):
        raise NotImplemented("Abstract method")

## @brief Abstract class to handle hierarchy relations
class _LeHierarch(_LeRelation):
    
    ## @brief modify a LeHierarch rank
    # @param new_rank int|str : The new rank can be an integer > 1 or strings 'first' or 'last'
    # @return True in case of success, False in case of failure
    # @throw ValueError if step is not castable into an integer
    def set_rank(self, new_rank):
        return self._set_rank(
                                new_rank,
                                id_superior=getattr(self, self.uidname()),
                                nature=self.nature
        )
    
    @classmethod
    def insert(cls, datas):
        # Checks if the relation exists
        datas[EditorialModel.classtypes.relation_name] = None
        res = cls.get(
                [(cls._subordinate_field_name, '=', datas['subordinate']), ('nature', '=', datas['nature'])],
                [ cls.uidname() ]
            )
        if not(res is None) and len(res) > 0:
            return False
        return super().insert(datas, 'LeHierarch')

    ## @brief Get maximum assignable rank given a superior id and a nature
    # @return an integer > 1
    @classmethod
    def get_max_rank(cls, id_superior, nature):
        if nature not in EditorialModel.classtypes.EmNature.getall():
            raise ValueError("Unknow relation nature '%s'" % nature)
        sql_res = cls.get(
                            query_filters=[
                                ('nature','=', nature),
                                (cls._superior_field_name, '=', id_superior),
                            ],
                            field_list=['rank'],
                            order=[('rank', 'DESC')],
                            limit=1,
                            instanciate=False
                        )
        return sql_res[0]['rank']+1 if not(sql_res is None) and len(sql_res) > 0 else 1

    ## @brief instanciate the relevant lodel object using a dict of datas
    @classmethod
    def object_from_data(cls, datas):
        return cls.name2class('LeHierarch')(**datas)

    ## @warning Abastract method
    def update(self):
        raise NotImplementedError("Abstract method")
        

## @brief Abstract class to handle rel2type relations
class _LeRel2Type(_LeRelation):
    ## @brief Stores the list of fieldtypes handling relations attributes
    _rel_attr_fieldtypes = dict()
    
    ## @brief Stores the LeClass child class used as superior
    _superior_cls = None
    ## @brief Stores the LeType child class used as subordinate
    _subordinate_cls = None
    ## @brief Stores the relation name for a rel2type
    _relation_name = None

    ## @brief modify a LeRel2Type rank
    # @param new_rank int|str : The new rank can be an integer > 1 or strings 'first' or 'last'
    # @return True in case of success, False in case of failure
    # @throw ValueError if step is not castable into an integer
    def set_rank(self, new_rank):
        if self._relation_name is None:
            raise NotImplementedError("Abstract method")
        return self._set_rank(new_rank, superior = self.superior, relation_name = self._relation_name)
    
    @classmethod
    def fieldtypes(cls, complete = True):
        ret = dict()
        if complete:
            ret.update(super().fieldtypes())
        ret.update(cls._rel_attr_fieldtypes)
        return ret

    @classmethod
    def get_max_rank(cls, superior, relation_name):
        # SELECT rank FROM relation JOIN object ON object.lodel_id = id_subordinate WHERE object.type_id = <type_em_id>
        ret = cls.get(
            query_filters = [
                (EditorialModel.classtypes.relation_name, '=', relation_name),
                (EditorialModel.classtypes.relation_superior, '=', superior),
            ],
            field_list = ['rank'],
            order = [('rank', 'DESC')],
            limit = 1,
            instanciate = False
        )
        return 1 if not ret else ret[0]['rank']

    ## @brief Implements insert for rel2type
    # @todo checks when autodetecing the rel2type class
    @classmethod
    def insert(cls, datas, classname = None):
        #Set the nature
        if 'nature' not in datas:
            datas['nature'] = None
        if cls.__name__ == 'LeRel2Type' and classname is None:
            if EditorialModel.classtypes.relation_name not in datas:
                raise RuntimeError("Unable to autodetect rel2type. No relation_name given")
            # autodetect the rel2type child class (BROKEN)
            classname = relname(datas[self._superior_field_name], datas[self._subordinate_field_name], datas[EditorialModel.classtypes.relation_name])
        else:
            if classname != None:
                ccls = cls.name2class(classname)
                if ccls == False:
                    raise lecrud.LeApiErrors("Bad classname given")
                relation_name = ccls._relation_name
            else:
                relation_name = cls._relation_name
            datas[EditorialModel.classtypes.relation_name] = relation_name
        return super().insert(datas, classname)

    ## @brief Given a superior and a subordinate, returns the classname of the give rel2type
    # @param lesupclass LeClass : LeClass child class (not an instance) (can be a LeType or a LeClass child)
    # @param lesubclass LeType : A LeType child class (not an instance)
    # @param relation_name str : Name of the relation (rel2type field name in LeClass)
    # @param cls
    # @return a name as string
    @classmethod
    def relname(cls, lesupclass, lesubclass, relation_name):
        supname = lesupclass._leclass.__name__ if lesupclass.implements_letype() else lesupclass.__name__
        subname = lesubclass.__name__
        return cls.name2rel2type(supname, subname, relation_name)

    ## @brief instanciate the relevant lodel object using a dict of datas
    @classmethod
    def object_from_data(cls, datas):
        le_object = cls.name2class('LeObject')
        class_name = le_object._me_uid[datas['class_id']].__name__
        type_name = le_object._me_uid[datas['type_id']].__name__
        relation_classname = lecrud._LeCrud.name2rel2type(class_name, type_name, datas[EditorialModel.classtypes.relation_name])

        del(datas['class_id'], datas['type_id'])

        return cls.name2class(relation_classname)(**datas)
