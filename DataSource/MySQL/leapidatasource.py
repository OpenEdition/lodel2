#-*- coding: utf-8 -*-

import pymysql
import copy

import leapi
from leapi.leobject import REL_SUB, REL_SUP

from leapi.lecrud import _LeCrud, REL_SUP, REL_SUB

from mosql.db import Database, all_to_dicts, one_to_dict
from mosql.query import select, insert, update, delete, join, left_join
from mosql.util import raw, or_
import mosql.mysql

from DataSource.dummy.leapidatasource import DummyDatasource
from DataSource.MySQL import utils
from EditorialModel.classtypes import EmNature

from Lodel.settings import Settings

## MySQL DataSource for LeObject
class LeDataSourceSQL(DummyDatasource):

    RELATIONS_POSITIONS_FIELDS = {REL_SUP: 'superior_id', REL_SUB: 'subordinate_id'}

    def __init__(self, module=pymysql, conn_args=None):
        super(LeDataSourceSQL, self).__init__()
        self.module = module
        if conn_args is None:
            conn_args = copy.copy(Settings.get('datasource')['default'])
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
    # @todo group: mosql does not permit direction in group_by clause, it should, so for now we don't use direction in group clause
    def select(self, target_cls, field_list, filters, rel_filters=None, order=None, group=None, limit=None, offset=None, instanciate=True):

        joins = []
        # it is a LeObject, query only on main table
        if target_cls.__name__ == 'LeObject':
            main_table = utils.common_tables['object']
            fields = [(main_table, target_cls.fieldlist())]

        # it is a LeType or a LeClass, query on main table left join class table on lodel_id
        elif target_cls.is_letype() or target_cls.is_leclass():
            # find main table
            main_table = utils.common_tables['object']
            main_class = target_cls.leo_class()
            # find class table
            class_table = utils.object_table_name(main_class.__name__)
            main_lodel_id = utils.column_prefix(main_table, main_class.uidname())
            class_lodel_id = utils.column_prefix(class_table, main_class.uidname())
            # do the join
            joins = [left_join(class_table, {main_lodel_id:class_lodel_id})]
            fields = [(main_table, target_cls.name2class('LeObject').fieldlist()), (class_table, main_class.fieldlist())]

        elif target_cls.is_lehierarch():
            main_table = utils.common_tables['relation']
            fields = [(main_table, target_cls.name2class('LeRelation').fieldlist())]
        elif target_cls.is_lerel2type():
            # find main table
            main_table = utils.common_tables['relation']
            # find relational table
            class_table = utils.r2t_table_name(target_cls._superior_cls.__name__, target_cls._subordinate_cls.__name__)
            relation_fieldname = target_cls.name2class('LeRelation').uidname()
            main_relation_id = utils.column_prefix(main_table, relation_fieldname)
            class_relation_id = utils.column_prefix(class_table, relation_fieldname)
            # do the joins
            lodel_id = target_cls.name2class('LeObject').uidname()
            joins = [
                left_join(class_table, {main_relation_id:class_relation_id}),
                # join with the object table to retrieve class and type of superior and subordinate
                left_join(utils.common_tables['object'] + ' as sup_obj', {'sup_obj.'+lodel_id:target_cls._superior_field_name}),
                left_join(utils.common_tables['object'] + ' as sub_obj', {'sub_obj.'+lodel_id:target_cls._subordinate_field_name})
            ]
            fields = [
                (main_table, target_cls.name2class('LeRelation').fieldlist()),
                (class_table, target_cls.fieldlist()),
                ('sup_obj', ['class_id']),
                ('sub_obj', ['type_id'])
            ]

            field_list.extend(['class_id', 'type_id'])
        else:
            raise AttributeError("Target class '%s' in get() is not a Lodel Editorial Object !" % target_cls)

        # prefix column name in fields list
        prefixed_field_list = [utils.find_prefix(name, fields) for name in field_list]

        kwargs = {}
        if group:
            kwargs['group_by'] = (utils.find_prefix(column, fields) for column, direction in group)
        if order:
            kwargs['order_by'] = (utils.find_prefix(column, fields) + ' ' + direction for column, direction in order)
        if limit:
            kwargs['limit'] = limit
        if offset:
            kwargs['offset'] = offset

        # relational filters
        # @todo this only works with hierarchy relations
        if rel_filters:
            le_relation = target_cls.name2class('LeRelation')
            rel_cpt = 0
            for rel_filter in rel_filters:
                rel_cpt += 1
                rel_name = 'rel' + str(rel_cpt)
                name, op, value = rel_filter
                direction, nature = name
                if direction == REL_SUP:
                    join_column, filter_column = (le_relation._subordinate_field_name, le_relation._superior_field_name)
                else:
                    join_column, filter_column = (le_relation._superior_field_name, le_relation._subordinate_field_name)
                rel_join = left_join(utils.common_tables['relation'] + ' as ' + rel_name, {utils.column_prefix(main_table, main_class.uidname()):utils.column_prefix(rel_name, join_column)})
                filters.append((utils.column_prefix(rel_name, 'nature'), '=', nature))
                filters.append((utils.column_prefix(rel_name, filter_column), op, value))
                joins.append(rel_join)

        # prefix filters'' column names, and prepare dict for mosql where {(fieldname, op): value}
        wheres = {(utils.find_prefix(name, fields), op):value for name,op,value in filters}
        query = select(main_table, select=prefixed_field_list, where=wheres, joins=joins, **kwargs)

        # Executing the query
        cur = utils.query(self.connection, query)
        results = all_to_dicts(cur)
        #print(results)

        # instanciate each row to editorial components
        if instanciate:
            results = [target_cls.object_from_data(datas) for datas in results]
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
    # @param target_cls LeCrud(class) : Instance of the object concerned by the update
    # @param filters list : List of filters (see @ref leobject_filters)
    # @param rel_filters list : List of relationnal filters (see @ref leobject_filters)
    # @param **datas : Datas in kwargs
    # @return the number of updated components
    # @todo implement other filters than lodel_id
    def update(self, target_cls, filters, rel_filters, **datas):
        class_table = False

        # it is a LeType
        if target_cls.is_letype():
            # find main table and main table datas
            main_table = utils.common_tables['object']
            main_datas = {target_cls.uidname(): raw(target_cls.uidname())} #  be sure to have one SET clause
            main_fields = target_cls.name2class('LeObject').fieldlist()
            class_table = utils.object_table_name(target_cls.leo_class().__name__)
        elif target_cls.is_lerel2type():
            main_table = utils.common_tables['relation']
            le_relation = target_cls.name2class('LeRelation')
            main_datas = {le_relation.uidname(): raw(le_relation.uidname())} #  be sure to have one SET clause
            main_fields = le_relation.fieldlist()

            class_table = utils.r2t_table_name(target_cls._superior_cls.__name__, target_cls._subordinate_cls.__name__)
        else:
            raise AttributeError("'%s' is not a LeType nor a LeRelation, it's impossible to update it" % target_cls)

        for main_column_name in main_fields:
            if main_column_name in datas:
                main_datas[main_column_name] = datas[main_column_name]
                del(datas[main_column_name])

        wheres = {(name, op):value for name,op,value in filters}
        sql = update(main_table, wheres, main_datas)
        utils.query(self.connection, sql)

        # update on class table
        if class_table and datas:
            sql = update(class_table, wheres, datas)
            utils.query(self.connection, sql)

        return True

    ## @brief inserts a new lodel editorial component
    # @param target_cls LeCrud(class) : The component class concerned by the insert (a LeCrud child class (not instance !) )
    # @param **datas : The datas to insert
    # @return The inserted component's id
    # @todo should work with LeType, LeClass, and Relations
    def insert(self, target_cls, **datas):
        class_table = False

        # it is a LeType
        if target_cls.is_letype():
            main_table = utils.common_tables['object']
            main_datas = {'class_id':target_cls.leo_class()._class_id, 'type_id':target_cls._type_id}
            main_fields = target_cls.name2class('LeObject').fieldlist()

            class_table = utils.object_table_name(target_cls.leo_class().__name__)
            fk_name = target_cls.uidname()
        # it is a hierarchy
        elif target_cls.is_lehierarch():
            main_table = utils.common_tables['relation']
            main_datas = {
                utils.column_name(target_cls._superior_field_name): datas[target_cls._superior_field_name].lodel_id,
                utils.column_name(target_cls._subordinate_field_name): datas[target_cls._subordinate_field_name].lodel_id
            }
            main_fields = target_cls.name2class('LeRelation').fieldlist()
        # it is a relation
        elif target_cls.is_lerel2type():
            main_table = utils.common_tables['relation']
            main_datas = {
                utils.column_name(target_cls._superior_field_name): datas[target_cls._superior_field_name].lodel_id,
                utils.column_name(target_cls._subordinate_field_name): datas[target_cls._subordinate_field_name].lodel_id
            }
            main_fields = target_cls.name2class('LeRelation').fieldlist()

            superior_class = datas['superior'].leo_class()
            class_table = utils.r2t_table_name(superior_class.__name__, datas['subordinate'].__class__.__name__)
            fk_name = superior_class.name2class('LeRelation').uidname()
        else:
            raise AttributeError("'%s' is not a LeType nor a LeRelation, it's impossible to insert it" % target_cls)

        # extract main table datas from datas
        for main_column_name in main_fields:
            if main_column_name in datas:
                if main_column_name not in main_datas:
                    main_datas[main_column_name] = datas[main_column_name]
                del(datas[main_column_name])

        sql = insert(main_table, main_datas)
        cur = utils.query(self.connection, sql)
        lodel_id = cur.lastrowid

        if class_table:
            # insert in class_table
            datas[fk_name] = lodel_id
            sql = insert(class_table, datas)
            utils.query(self.connection, sql)

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

    ## @brief Sets a new rank on a relation
    # @param le_relation LeRelation
    # @param new_rank int: integer representing the absolute new rank
    # @return True if success, False if failure
    # TODO Conserver cette méthode dans le datasource du fait des requêtes SQL. Elle est appelée par le set_rank de LeRelation
    def update_rank(self, le_relation, rank):

        lesup = le_relation.id_sup
        lesub = le_relation.id_sub
        current_rank = le_relation.rank

        relations = le_relation.__class__.get(query_filters=[('id_sup', '=', lesup)], order=[('rank', 'ASC')])
        # relations = self.get_related(lesup, lesub.__class__, get_sub=True)

        # insert the relation at the right position considering its new rank
        our_relation = relations.pop(current_rank)
        relations.insert(our_relation, rank)

        # rebuild now the list of relations from the resorted list and recalculating the ranks
        rdatas = [(attrs['relation_id'], new_rank+1) for new_rank, (sup, sub, attrs) in enumerate(relations)]

        sql = insert(MySQL.relations_table_name, columns=(MySQL.relations_pkname, 'rank'), values=rdatas, on_duplicate_key_update={'rank', mosql.util.raw('VALUES(`rank`)')})
        with self.connection as cur:
            if cur.execute(sql) != 1:
                return False
            else:
                return True
