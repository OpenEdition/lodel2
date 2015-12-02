#-*- coding: utf-8 -*-

import pymysql
import copy

import leapi
from leapi.leobject import REL_SUB, REL_SUP

from leapi.lecrud import _LeCrud

from mosql.db import Database, all_to_dicts, one_to_dict
from mosql.query import select, insert, update, delete, join, left_join
from mosql.util import raw, or_
import mosql.mysql

from DataSource.dummy.leapidatasource import DummyDatasource
from DataSource.MySQL.common_utils import MySQL
from EditorialModel.classtypes import EmNature, common_fields


## MySQL DataSource for LeObject
class LeDataSourceSQL(DummyDatasource):

    RELATIONS_POSITIONS_FIELDS = {REL_SUP: 'superior_id', REL_SUB: 'subordinate_id'}

    def __init__(self, module=pymysql, conn_args=None):
        super(LeDataSourceSQL, self).__init__()
        self.module = module
        self.datasource_utils = MySQL
        if conn_args is None:
            conn_args = copy.copy(self.datasource_utils.connections['default'])
            self.module = conn_args['module']
            del conn_args['module']
        self.connection = Database(self.module, **conn_args)

    ## @brief select lodel editorial components using given filters
    # @param target_cls LeCrud(class): The component class concerned by the select (a LeCrud child class (not instance !) )
    # @param field_list list: List of field to fetch
    # @param filters list: List of filters (see @ref lecrud_filters)
    # @param rel_filters list: List of relational filters (see @ref lecrud_filters)
    # @return a list of LeCrud child classes
    # @todo this only works with LeObject.get(), LeClass.get() and LeType.get()
    # @todo for speed get rid of all_to_dicts
    # @todo filters: all use cases are not implemented
    def select(self, target_cls, field_list, filters, rel_filters=None):

        joins = []
        # it is a LeObject, query only on main table
        if target_cls.__name__ == 'LeObject':
            main_table = self.datasource_utils.objects_table_name
            fields = [(main_table, common_fields)]

        # it is a LeType or a LeClass, query on main table left join class table on lodel_id
        elif target_cls.is_letype() or target_cls.is_leclass():
            # find main table and main table datas
            main_table = self.datasource_utils.objects_table_name
            main_class = target_cls._leclass if hasattr(target_cls, '_leclass') else target_cls
            class_table = self.datasource_utils.get_table_name_from_class(main_class.__name__)
            main_lodel_id = self.datasource_utils.column_prefix(main_table, self.datasource_utils.field_lodel_id)
            class_lodel_id = self.datasource_utils.column_prefix(class_table, self.datasource_utils.field_lodel_id)
            joins = [left_join(class_table, {main_lodel_id:class_lodel_id})]
            fields = [(main_table, common_fields), (class_table, main_class.fieldlist())]

        # prefix column name in field list
        prefixed_field_list = [self.datasource_utils.find_prefix(name, fields) for name in field_list]

        # @todo implement that
        #if rel_filters is not None and len(rel_filters) > 0:
            #rel_filters = self._prepare_rel_filters(rel_filters)
            #for rel_filter in rel_filters:
                ## join condition
                #relation_table_join_field = "%s.%s" % (self.datasource_utils.relations_table_name, self.RELATIONS_POSITIONS_FIELDS[rel_filter['position']])
                #query_table_join_field = "%s.%s" % (query_table_name, self.datasource_utils.relations_field_nature)
                #join_fields[query_table_join_field] = relation_table_join_field
                ## adding "where" filters
                #where_filters['%s.%s' % (self.datasource_utils.relations_table_name, self.datasource_utils.relations_field_nature)] = rel_filter['nature']
                #where_filters[rel_filter['condition_key']] = rel_filter['condition_value']

        # prefix filters'' column names, and prepare dict for mosql where {(fieldname, op): value}
        wheres = {(self.datasource_utils.find_prefix(name, fields), op):value for name,op,value in filters}
        query = select(main_table, select=prefixed_field_list, where=wheres, joins=joins)
        #print ('SQL', query)

        # Executing the query
        cur = self.datasource_utils.query(self.connection, query)
        results = all_to_dicts(cur)

        # instanciate each row to editorial components
        results = [target_cls.uid2leobj(datas['type_id'])(**datas) for datas in results]
        #print('results', results)

        return results

    ## @brief delete lodel editorial components given filters
    # @param target_cls LeCrud(class): The component class concerned by the delete (a LeCrud child class (not instance !) )
    # @param filters list : List of filters (see @ref leobject_filters)
    # @param rel_filters list : List of relational filters (see @ref leobject_filters)
    # @return the number of deleted components
    def delete(self, target_cls, filters, rel_filters):
        query_table_name = self.datasource_utils.get_table_name_from_class(target_cls.__name__)
        prep_filters = self._prepare_filters(filters, query_table_name)
        prep_rel_filters = self._prepare_rel_filters(rel_filters)

        if len(prep_rel_filters) > 0:
            query = "DELETE %s FROM" % query_table_name
            for prep_rel_filter in prep_rel_filters:
                query += "%s INNER JOIN %s ON (%s.%s = %s.%s)" % (
                    self.datasource_utils.relations_table_name,
                    query_table_name,
                    self.datasource_utils.relations_table_name,
                    prep_rel_filter['position'],
                    query_table_name,
                    self.datasource_utils.field_lodel_id
                )

                if prep_rel_filter['condition_key'][0] is not None:
                    prep_filters[("%s.%s" % (self.datasource_utils.relations_table_name, prep_rel_filter['condition_key'][0]), prep_rel_filter['condition_key'][1])] = prep_rel_filter['condition_value']

            if prep_filters is not None and len(prep_filters) > 0:
                query += " WHERE "
                filter_counter = 0
                for filter_item in prep_filters:
                    if filter_counter > 1:
                        query += " AND "
                    query += "%s %s %s" % (filter_item[0][0], filter_item[0][1], filter_item[1])
        else:
            query = delete(query_table_name, prep_filters)

        query_delete_from_object = delete(self.datasource_utils.objects_table_name, {'lodel_id': filters['lodel_id']})
        with self.connection as cur:
            result = cur.execute(query)
            cur.execute(query_delete_from_object)

        return result

    ## @brief update an existing lodel editorial component
    # @param target_cls LeCrud(class) : The component class concerned by the update (a LeCrud child class (not instance !) )
    # @param filters list : List of filters (see @ref leobject_filters)
    # @param rel_filters list : List of relationnal filters (see @ref leobject_filters)
    # @param **datas : Datas in kwargs
    # @return the number of updated components
    # @todo implement other filters than lodel_id
    def update(self, target_cls, filters, rel_filters, **datas):
        print(target_cls, filters, rel_filters, datas)
        # it is a LeType
        if not target_cls.is_letype():
            raise AttributeError("'%s' is not a LeType, it is not possible to update it" % target_cls)

        # find main table and main table datas
        main_table = self.datasource_utils.objects_table_name
        main_datas = {self.datasource_utils.field_lodel_id: raw(self.datasource_utils.field_lodel_id)} #  be sure to have one SET clause
        for main_column_name in common_fields:
            if main_column_name in datas:
                main_datas[main_column_name] = datas[main_column_name]
                del(datas[main_column_name])

        wheres = {(name, op):value for name,op,value in filters}
        query = update(main_table, wheres, main_datas)
        #print(query)
        self.datasource_utils.query(self.connection, query)

        # update on class table
        if datas:
            class_table = self.datasource_utils.get_table_name_from_class(target_cls._leclass.__name__)
            query = update(class_table, wheres, datas)
            #print(query)
            self.datasource_utils.query(self.connection, query)

        return True

    ## @brief inserts a new lodel editorial component
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param **datas : The datas to insert
    # @return The inserted component's id
    # @todo should work with LeType, LeClass, and Relations
    def insert(self, target_cls, **datas):
        # it is a LeType
        if not target_cls.is_letype():
            raise AttributeError("'%s' is not a LeType, it is not possible to insert it" % target_cls)

        # find main table and main table datas
        main_table = self.datasource_utils.objects_table_name
        main_datas = {'class_id':target_cls._leclass._class_id, 'type_id':target_cls._type_id}
        for main_column_name in common_fields:
            if main_column_name in datas:
                main_datas[main_column_name] = datas[main_column_name]
                del(datas[main_column_name])

        cur = self.datasource_utils.query(self.connection, insert(main_table, main_datas))
        lodel_id = cur.lastrowid

        # insert in class_table
        datas[self.datasource_utils.field_lodel_id] = lodel_id
        class_table = self.datasource_utils.get_table_name_from_class(target_cls._leclass.__name__)
        self.datasource_utils.query(self.connection, insert(class_table, datas))

        return lodel_id

    ## @brief insert multiple editorial component
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param datas_list list : A list of dict representing the datas to insert
    # @return int the number of inserted component
    def insert_multi(self, target_cls, datas_list):
        res = list()
        for data in datas_list:
            res.append(self.insert(target_cls, data))
        return len(res)

    ## @brief prepares the relational filters
    # @params rel_filters : (("superior"|"subordinate"), operator, value)
    # @return list
    def _prepare_rel_filters(self, rel_filters):
        prepared_rel_filters = []

        if rel_filters is not None and len(rel_filters) > 0:
            for rel_filter in rel_filters:
                rel_filter_dict = {
                    'position': REL_SUB if rel_filter[0][0] == REL_SUP else REL_SUB,
                    'nature': rel_filter[0][1],
                    'condition_key': (self.RELATIONS_POSITIONS_FIELDS[rel_filter[0][0]], rel_filter[1]),
                    'condition_value': rel_filter[2]
                }
                prepared_rel_filters.append(rel_filter_dict)

        return prepared_rel_filters

    ## @brief prepares the filters to be used by the mosql library's functions
    # @params filters : (FIELD, OPERATOR, VALUE) tuples
    # @return dict : Dictionnary with (FIELD, OPERATOR):VALUE style elements
    def _prepare_filters(self, filters, tablename=None):
        prepared_filters = {}
        if filters is not None and len(filters) > 0:
            for filter_item in filters:
                if '.' in filter_item[0]:
                    prepared_filter_key = (filter_item[0], filter_item[1])
                else:
                    prepared_filter_key = ("%s.%s" % (tablename, filter_item[0]), filter_item[1])
                prepared_filter_value = filter_item[2]
                prepared_filters[prepared_filter_key] = prepared_filter_value

        return prepared_filters

    # ================================================================================================================ #
    # FONCTIONS A DEPLACER                                                                                             #
    # ================================================================================================================ #

    ## @brief Make a relation between 2 LeType
    # @note rel2type relations. Superior is the LeType from the EmClass and subordinate the LeType for the EmType
    # @param lesup LeType : LeType child class instance that is from the EmClass containing the rel2type field
    # @param lesub LeType : LeType child class instance that is from the EmType linked by the rel2type field ( @ref EditorialModel.fieldtypes.rel2type.EmFieldType.rel_to_type_id )
    # @return The relation_id if success else return False
    def add_related(self, lesup, lesub, rank, **rel_attr):
        with self.connection as cur:
            #First step : relation table insert
            sql = insert(MySQL.relations_table_name, {
                'id_sup': lesup.lodel_id,
                'id_sub': lesub.lodel_id,
                'rank': 0,  # default value that will be set latter
            })
            cur.execute(sql)
            relation_id = cur.lastrowid

            if len(rel_attr) > 0:
                #There is some relation attribute to add in another table
                attr_table = get_r2t2table_name(lesup._leclass.__name__, lesub.__class__.__name__)
                rel_attr['id_relation'] = relation_id
                sql = insert(attr_table, rel_attr)
                cur.execute(sql)
        self._set_relation_rank(id_relation, rank)
        return relation_id

    ## @brief Deletes the relation between 2 LeType
    # @param lesup LeType
    # @param lesub LeType
    # @param fields dict
    # @return True if success else False
    # @todo Add fields parameter to identify relation
    # @todo Delete relationnal fields if some exists
    def del_related(self, lesup, lesub, fields=None):
        with self.connection as cur:
            del_params = {
                'id_sup': lesup.lodel_id,
                'id_sub': lesub.lodel_id
            }
            delete_params = {}

            if fields is not None:
                delete_params = del_params.copy()
                delete_params.update(fields)
            else:
                delete_params = del_params

            sql = delete(
                self.datasource_utils.relations_table_name,
                delete_params
            )

            if cur.execute(sql) != 1:
                return False

        return True

    ## @brief Fetch related (rel2type) by LeType
    # @param leo LeType : We want related LeObject of this LeType child class instance
    # @param letype LeType(class) : We want related LeObject of this LeType child class (not instance)
    # @param get_sub bool : If True leo is the superior and we want subordinates, else its the opposite
    # @return a list of dict { 'id_relation':.., 'rank':.., 'lesup':.., 'lesub'.., 'rel_attrs': dict() }
    def get_related(self, leo, letype, get_sub=True):
        if LeCrud.name2class('LeType') not in letype.__bases__:
            raise ValueError("letype argument should be a LeType child class, but got %s" % type(letype))

        if not isinstance(leo, LeType):
            raise ValueError("leo argument should be a LeType child class instance but got %s" % type(leo))
        with self.connection as cur:
            id_leo, id_type = 'id_sup', 'id_sub' if get_sub else 'id_sub', 'id_sup'

            joins = [
                join(
                    (MySQL.objects_table_name, 'o'),
                    on={'r.' + id_type: 'o.' + MySQL.field_lodel_id}
                ),
                join(
                    (MySQL.objects_table_name, 'p'),
                    on={'r.' + id_leo: 'p.' + MySQL.field_lodel_id}
                ),
            ]

            lesup, lesub = leo.__class__, letype if get_sub else letype, leo.__class__
            common_infos = ('r.id_relation', 'r.id_sup', 'r.id_sub', 'r.rank', 'r.depth')
            if len(lesup._linked_types[lesub]) > 0:
                #relationnal attributes, need to join with r2t table
                cls_name = leo.__class__.__name__ if get_sub else letype.__name__
                type_name = letype.__name__ if get_sub else leo.__class__.__name__
                joins.append(
                    join(
                        (MySQL.get_r2t2table_name(cls_name, type_name), 'r2t'),
                        on={'r.' + MySQL.relations_pkname: 'r2t' + MySQL.relations_pkname}
                    )
                )
                select = ('r.id_relation', 'r.id_sup', 'r.id_sub', 'r.rank', 'r.depth', 'r2t.*')
            else:
                select = common_infos

            sql = select(
                (MySQL.relations_table_name, 'r'),
                select=select,
                where={
                    id_leo: leo.lodel_id,
                    'type_id': letype._type_id,
                },
                joins=joins
            )

            cur.execute(sql)
            res = all_to_dicts(cur)

            #Building result
            ret = list()
            for datas in res:
                r_letype = letype(res['r.' + id_type])
                ret_item = {
                    'id_relation': +datas[MySQL.relations_pkname],
                    'lesup': r_leo if get_sub else r_letype,
                    'lesub': r_letype if get_sub else r_leo,
                    'rank': res['rank']
                }

                rel_attr = copy.copy(datas)
                for todel in common_infos:
                    del rel_attr[todel]
                ret_item['rel_attrs'] = rel_attr
                ret.append(ret_item)

            return ret

    ## @brief Set the rank of a relation identified by its ID
    # @param id_relation int : relation ID
    # @param rank int|str : 'first', 'last', or an integer value
    # @throw ValueError if rank is not valid
    # @throw leapi.leapi.LeObjectQueryError if id_relation don't exists
    def set_relation_rank(self, id_relation, rank):
        self._check_rank(rank)
        self._set_relation_rank(id_relation, rank)

    ## @brief Set the rank of a relation identified by its ID
    #
    # @note this solution is not the more efficient solution but it
    # garantee that ranks are continuous and starts at 1
    # @warning there is no way to fail on rank parameters even giving very bad parameters, if you want a method that may fail on rank use set_relation_rank() instead
    # @param id_relation int : relation ID
    # @param rank int|str : 'first', 'last', or an integer value
    # @throw leapi.leapi.LeObjectQueryError if id_relation don't exists
    def _set_relation_rank(self, id_relation, rank):
        ret = self.get_relation(id_relation, no_attr=True)
        if not ret:
            raise leapi.leapi.LeObjectQueryError("No relation with id_relation = %d" % id_relation)
        lesup = ret['lesup']
        lesub = ret['lesup']
        cur_rank = ret['rank']
        rank = 1 if rank == 'first' or rank < 1 else rank
        if cur_rank == rank:
            return True

        relations = self.get_related(lesup, lesub.__class__, get_sub=True)

        if not isinstance(rank, int) or rank > len(relations):
            rank = len(relations)
            if cur_rank == rank:
                return True

        #insert the relation at the good position
        our_relation = relations.pop(cur_rank)
        relations.insert(our_relation, rank)

        #gathering (relation_id, new_rank)
        rdatas = [(attrs['relation_id'], new_rank + 1) for new_rank, (sup, sub, attrs) in enumerate(relations)]
        sql = insert(MySQL.relations_table_name, columns=(MySQL.relations_pkname, 'rank'), values=rdatas, on_duplicate_key_update={'rank', mosql.util.raw('VALUES(`rank`)')})

    ## @brief Check a rank value
    # @param rank int | str : Can be an integer >= 1 , 'first' or 'last'
    # @throw ValueError if the rank is not valid
    def _check_rank(self, rank):
        if isinstance(rank, str) and rank != 'first' and rank != 'last':
            raise ValueError("Invalid rank value : %s" % rank)
        elif isinstance(rank, int) and rank < 1:
            raise ValueError("Invalid rank value : %d" % rank)
        else:
            raise ValueError("Invalid rank type : %s" % type(rank))

    ## @brief Link two object given a relation nature, depth and rank
    # @param lesup LeObject : a LeObject
    # @param lesub LeObject : a LeObject
    # @param nature str|None : The relation nature or None if rel2type
    # @param rank int : a rank
    def add_relation(self, lesup, lesub, nature=None, depth=None, rank=None, **rel_attr):
        if len(rel_attr) > 0 and nature is not None:
            #not a rel2type but have some relation attribute
            raise AttributeError("No relation attributes allowed for non rel2type relations")

        with self.connection as cur:
            sql = insert(self.datasource_utils.relations_table_name, {'id_sup': lesup.lodel_id, 'id_sub': lesub.lodel_id, 'nature': nature, 'rank': rank, 'depth': depth})
            if cur.execute(sql) != 1:
                raise RuntimeError("Unknow SQL error")

            if len(rel_attr) > 0:
                #a relation table exists
                cur.execute('SELECT last_insert_id()')
                relation_id, = cur.fetchone()
                raise NotImplementedError()

        return True

    ## @brief Delete a relation
    # @warning this method may not be efficient
    # @param id_relation int : The relation identifier
    # @return bool
    def del_relation(self, id_relation):
        with self.connection as cur:
            pk_where = {MySQL.relations_pkname: id_relation}
            if not MySQL.fk_on_delete_cascade and len(lesup._linked_types[lesub.__class__]) > 0:
                #Delete the row in the relation attribute table
                ret = self.get_relation(id_relation, no_attr=False)
                lesup = ret['lesup']
                lesub = ret['lesub']
                sql = delete(MySQL.relations_table_name, pk_where)
                if cur.execute(sql) != 1:
                    raise RuntimeError("Unknown SQL Error")
            sql = delete(MySQL.relations_table_name, pk_where)
            if cur.execute(sql) != 1:
                raise RuntimeError("Unknown SQL Error")

        return True

    ## @brief Fetch a relation
    # @param id_relation int : The relation identifier
    # @param no_attr bool : If true dont fetch rel_attr
    # @return a dict{'id_relation':.., 'lesup':.., 'lesub':..,'rank':.., 'depth':.., #if not none#'nature':.., #if exists#'dict_attr':..>}
    #
    # @todo TESTS
    def get_relation(self, id_relation, no_attr=False):
        relation = dict()
        with self.connection as cur:
            sql = select(MySQL.relation_table_name, {MySQL.relations_pkname: id_relation})
            if cur.execute(sql) != 1:
                raise RuntimeError("Unknow SQL error")
            res = all_to_dicts(cur)
            if len(res) == 0:
                return False
            if len(res) > 1:
                raise RuntimeError("When selecting on primary key, get more than one result. Bailout")

            if res['nature'] is not None:
                raise ValueError("The relation with id %d is not a rel2type relation" % id_relation)

            leobj = leapi.lefactory.LeFactory.leobj_from_name('LeObject')
            lesup = leobj.uid2leobj(res['id_sup'])
            lesub = leobj.uid2leobj(res['id_sub'])

            relation['id_relation'] = res['id_relation']
            relation['lesup'] = lesup
            relation['lesub'] = lesub
            relation['rank'] = rank
            relation['depth'] = depth
            if res['nature'] is not None:
                relation['nature'] = res['nature']

            if not no_attr and res['nature'] is None and len(lesup._linked_types[lesub.__class__]) != 0:
                #Fetch relation attributes
                rel_attr_table = MySQL.get_r2t2table_name(lesup.__class__.__name__, lesub.__class__.__name__)
                sql = select(MySQL.rel_attr_table, {MySQL.relations_pkname: id_relation})
                if cur.execute(sql) != 1:
                    raise RuntimeError("Unknow SQL error")

                res = all_to_dicts(cur)
                if len(res) == 0:
                    #Here raising a warning and adding empty (or default) attributes will be better
                    raise RuntimeError("This relation should have attributes but none found !!!")
                if len(res) > 1:
                    raise RuntimeError("When selecting on primary key, get more than one result. Bailout")
                attrs = res[0]
            relation['rel_attr'] = attrs

            return relation

    ## @brief Fetch all relations concerning an object (rel2type relations)
    # @param leo LeType : LeType child instance
    # @return a list of tuple (lesup, lesub, dict_attr)
    def get_relations(self, leo):

        sql = select(self.datasource_utils.relations_table_name, where=or_(({'id_sub': leo.lodel_id}, {'id_sup': leo.lodel_id})))

        with self.connection as cur:
            results = all_to_dicts(cur.execute(sql))

        relations = []
        for result in results:
            id_sup = result['id_sup']
            id_sub = result['id_sub']

            del result['id_sup']
            del result['id_sub']
            rel_attr = result

            relations.append((id_sup, id_sub, rel_attr))

        return relations

    ## @brief Add a superior to a LeObject
    # @note in the MySQL version the method will have a depth=None argument to allow reccursive calls to add all the path to the root with corresponding depth
    # @param lesup LeType : superior LeType child class instance
    # @param lesub LeType : subordinate LeType child class instance
    # @param nature str : A relation nature @ref EditorialModel.classtypesa
    # @param rank int : The rank of this relation
    # @param depth None|int : The depth of the relation (used to make reccursive calls in order to link with all superiors)
    # @return The relation ID or False if fails
    def add_superior(self, lesup, lesub, nature, rank, depth=None):

        params = {'id_sup': lesup.lodel_id, 'id_sub': lesub.lodel_id, 'nature': nature, 'rank': rank}
        if depth is not None:
            params['depth'] = depth

        sql_insert = insert(self.datasource_utils.relations_table_name, params)
        with self.connection as cur:
            if cur.execute(sql_insert) != 1:
                return False

            cur.execute('SELECT last_insert_id()')
            relation_id, = cur.fetchone()

        if nature in EmNature.getall():
            parent_superiors = lesup.superiors()
            for superior in parent_superiors:
                depth = depth - 1 if depth is not None else 1
                self.add_relation(lesup=superior.lodel_id, lesub=lesub.lodel_id, nature=nature, depth=depth, rank=rank)

        return relation_id

    ## @brief Fetch a superiors list ordered by depth for a LeType
    # @param lesub LeType : subordinate LeType child class instance
    # @param nature str : A relation nature @ref EditorialModel.classtypes
    # @return A list of LeType ordered by depth (the first is the direct superior)
    def get_superiors(self, lesub, nature):

        sql = select(
            self.datasource_utils.relations_table_name,
            columns=('id_sup',),
            where={'id_sub': lesub.lodel_id, 'nature': nature},
            order_by=('depth desc',)
        )

        result = []
        with self.connection as cur:
            results = all_to_dicts(cur.execute(sql))

        superiors = [LeType(result['id_sup']) for result in results]

        return superiors

    ## @brief Fetch the list of the subordinates given a nature
    # @param lesup LeType : superior LeType child class instance
    # @param nature str : A relation nature @ref EditorialModel.classtypes
    # @return A list of LeType ordered by rank that are subordinates of lesup in a "nature" relation
    def get_subordinates(self, lesup, nature):
        with self.connection as cur:
            id_sup = lesup.lodel_id if isinstance(lesup, leapi.letype.LeType) else MySQL.leroot_lodel_id
            sql = select(
                MySQL.relations_table_name,
                columns=('id_sup',),
                where={'id_sup': id_sup, 'nature': nature},
                order_by=('rank',)
            )
            cur.execut(sql)
            res = all_to_dicts(cur)

            return [LeType(r['id_sup']) for r in res]

    # ================================================================================================================ #
    # FONCTIONS A SUPPRIMER                                                                                            #
    # ================================================================================================================ #

    ## @brief inserts a new object
    # @param letype LeType
    # @param leclass LeClass
    # @param datas dict : dictionnary of field:value pairs to save
    # @return int : lodel_id of the created object
    # @todo add the returning clause and the insertion in "object"
    # def insert(self, letype, leclass, datas):
    #     if isinstance(datas, list):
    #         res = list()
    #         for data in datas:
    #             res.append(self.insert(letype, leclass, data))
    #         return res if len(res)>1 else res[0]
    #     elif isinstance(datas, dict):
    #
    #         object_datas = {'class_id': leclass._class_id, 'type_id': letype._type_id}
    #
    #         cur = self.datasource_utils.query(self.connection, insert(self.datasource_utils.objects_table_name, object_datas))
    #         lodel_id = cur.lastrowid
    #
    #         datas[self.datasource_utils.field_lodel_id] = lodel_id
    #         query_table_name = self.datasource_utils.get_table_name_from_class(leclass.__name__)
    #         self.datasource_utils.query(self.connection, insert(query_table_name, datas))
    #
    #         return lodel_id

    ## @brief search for a collection of objects
    # @param leclass LeClass
    # @param letype LeType
    # @field_list list
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relation_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @return list
    # def get(self, leclass, letype, field_list, filters, relational_filters=None):
    #
    #     if leclass is None:
    #         query_table_name = self.datasource_utils.objects_table_name
    #     else:
    #         query_table_name = self.datasource_utils.get_table_name_from_class(leclass.__name__)
    #     where_filters = self._prepare_filters(filters, query_table_name)
    #     join_fields = {}
    #
    #     if relational_filters is not None and len(relational_filters) > 0:
    #         rel_filters = self._prepare_rel_filters(relational_filters)
    #         for rel_filter in rel_filters:
    #           # join condition
    #           relation_table_join_field = "%s.%s" % (self.datasource_utils.relations_table_name, self.RELATIONS_POSITIONS_FIELDS[rel_filter['position']])
    #            query_table_join_field = "%s.%s" % (query_table_name, self.datasource_utils.field_lodel_id)
    #            join_fields[query_table_join_field] = relation_table_join_field
    #           # Adding "where" filters
    #            where_filters['%s.%s' % (self.datasource_utils.relations_table_name, self.datasource_utils.relations_field_nature)] = rel_filter['nature']
    #            where_filters[rel_filter['condition_key']] = rel_filter['condition_value']
            #
    #       # building the query
            # query = select(query_table_name, where=where_filters, select=field_list, joins=join(self.datasource_utils.relations_table_name, join_fields))
        # else:
        #     query = select(query_table_name, where=where_filters, select=field_list)
        #
        # Executing the query
        # cur = self.datasource_utils.query(self.connection, query)
        # results = all_to_dicts(cur)
        #
        # return results

    ## @brief delete an existing object
    # @param letype LeType
    # @param leclass LeClass
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @return bool : True on success
    # def delete(self, letype, leclass, filters, relational_filters):
    #     query_table_name = self.datasource_utils.get_table_name_from_class(leclass.__name__)
    #     prep_filters = self._prepare_filters(filters, query_table_name)
    #     prep_rel_filters = self._prepare_rel_filters(relational_filters)
    #
    #     if len(prep_rel_filters) > 0:
    #         query = "DELETE %s FROM " % query_table_name
    #
    #         for prep_rel_filter in prep_rel_filters:
    #             query += "%s INNER JOIN %s ON (%s.%s = %s.%s)" % (
    #                 self.datasource_utils.relations_table_name,
    #                 query_table_name,
    #                 self.datasource_utils.relations_table_name,
    #                 prep_rel_filter['position'],
    #                 query_table_name,
    #                 self.datasource_utils.field_lodel_id
    #             )
    #
    #             if prep_rel_filter['condition_key'][0] is not None:
    #                 prep_filters[("%s.%s" % (self.datasource_utils.relations_table_name, prep_rel_filter['condition_key'][0]), prep_rel_filter['condition_key'][1])] = prep_rel_filter['condition_value']
    #
    #         if prep_filters is not None and len(prep_filters) > 0:
    #             query += " WHERE "
    #             filter_counter = 0
    #             for filter_item in prep_filters:
    #                 if filter_counter > 1:
    #                     query += " AND "
    #                 query += "%s %s %s" % (filter_item[0][0], filter_item[0][1], filter_item[1])
    #     else:
    #         query = delete(query_table_name, filters)
    #
    #     query_delete_from_object = delete(self.datasource_utils.objects_table_name, {'lodel_id': filters['lodel_id']})
    #     with self.connection as cur:
    #         cur.execute(query)
    #         cur.execute(query_delete_from_object)
    #
    #     return True

    ## @brief update an existing object's data
    # @param letype LeType
    # @param leclass LeClass
    # @param  filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param rel_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @param data dict
    # @return bool
    # @todo prendre en compte les rel_filters
    # def update(self, letype, leclass, filters, rel_filters, data):
    #
    #     query_table_name = self.datasource_utils.get_table_name_from_class(leclass.__name__)
    #     where_filters = filters
    #     set_data = data
    #
    #     prepared_rel_filters = self._prepare_rel_filters(rel_filters)
    #
        # Building the query
        # query = update(table=query_table_name, where=where_filters, set=set_data)
        # Executing the query
        # with self.connection as cur:
        #     cur.execute(query)
        # return True
