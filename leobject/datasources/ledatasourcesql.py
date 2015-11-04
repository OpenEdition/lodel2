#-*- coding: utf-8 -*-

import pymysql

from leobject.datasources.dummy import DummyDatasource
from leobject.leobject import REL_SUB, REL_SUP

from mosql.db import Database, all_to_dicts
from mosql.query import select, insert, update, delete, join
from mosql.util import raw
import mosql.mysql
from DataSource.MySQL.MySQL import MySQL


## MySQL DataSource for LeObject
class LeDataSourceSQL(DummyDatasource):

    RELATIONS_POSITIONS_FIELDS = {REL_SUP: 'superior_id', REL_SUB: 'subordinate_id'}

    def __init__(self, module=pymysql, conn_args=None):
        super(LeDataSourceSQL, self).__init__()
        self.module = module
        self.datasource_utils = MySQL
        if conn_args is None:
            conn_args = self.datasource_utils.connections['default']
        self.connection = Database(self.module, host=conn_args['host'], user=conn_args['user'], passwd=conn_args['passwd'], db=conn_args['db'])

    ## @brief inserts a new object
    # @param letype LeType
    # @param leclass LeClass
    # @param datas dict : dictionnary of field:value pairs to save
    # @return int : lodel_id of the created object
    # @todo add the returning clause and the insertion in "object"
    def insert(self, letype, leclass, datas):
        if isinstance(datas, list):
            res = list()
            for data in datas:
                res.append(self.insert(letype, leclass, data))
            return res
        elif isinstance(datas, dict):

            with self.connection as cur:
                object_datas = {'class_id': leclass._class_id, 'type_id': letype._type_id}
                if cur.execute(insert(self.datasource_utils.objects_table_name, object_datas)) != 1:
                    raise RuntimeError('SQL error')

                if cur.execute('SELECT last_insert_id() as lodel_id') != 1:
                    raise RuntimeError('SQL error')

                lodel_id, = cur.fetchone()

                datas[self.datasource_utils.field_lodel_id] = lodel_id
                query_table_name = self.datasource_utils.get_table_name_from_class(leclass.__name__)
                query = insert(query_table_name, datas)

                if cur.execute(query) != 1:
                    raise RuntimeError('SQL error')

            return lodel_id

    ## @brief search for a collection of objects
    # @param leclass LeClass
    # @param letype LeType
    # @field_list list
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relation_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @return list
    def get(self, leclass, letype, field_list, filters, relational_filters=None):

        query_table_name = self.datasource_utils.get_table_name_from_class(leclass.__name__)
        where_filters = self._prepare_filters(filters, query_table_name)
        join_fields = {}

        if relational_filters is not None and len(relational_filters) > 0:
            rel_filters = self._prepare_rel_filters(relational_filters)
            for rel_filter in rel_filters:
                # join condition
                relation_table_join_field = "%s.%s" % (self.datasource_utils.relations_table_name, self.RELATIONS_POSITIONS_FIELDS[rel_filter['position']])
                query_table_join_field = "%s.%s" % (query_table_name, self.datasource_utils.field_lodel_id)
                join_fields[query_table_join_field] = relation_table_join_field
                # Adding "where" filters
                where_filters['%s.%s' % (self.datasource_utils.relations_table_name, self.datasource_utils.relations_field_nature)] = rel_filter['nature']
                where_filters[rel_filter['condition_key']] = rel_filter['condition_value']

            # building the query
            query = select(query_table_name, where=where_filters, select=field_list, joins=join(self.datasource_utils.relations_table_name, join_fields))
        else:
            query = select(query_table_name, where=where_filters, select=field_list)

        # Executing the query
        with self.connection as cur:
            results = all_to_dicts(cur.execute(query))

        return results

    ## @brief delete an existing object
    # @param letype LeType
    # @param leclass LeClass
    # @param filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param relational_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @return bool : True on success
    def delete(self, letype, leclass, filters, relational_filters):
        query_table_name = self.datasource_utils.get_table_name_from_class(leclass.__name__)
        prep_filters = self._prepare_filters(filters, query_table_name)
        prep_rel_filters = self._prepare_rel_filters(relational_filters)

        if len(prep_rel_filters) > 0:
            query = "DELETE %s FROM " % query_table_name

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
            query = delete(query_table_name, filters)

        query_delete_from_object = delete(self.datasource_utils.objects_table_name, {'lodel_id': filters['lodel_id']})
        with self.connection as cur:
            cur.execute(query)
            cur.execute(query_delete_from_object)

        return True

    ## @brief update an existing object's data
    # @param letype LeType
    # @param leclass LeClass
    # @param  filters list : list of tuples formatted as (FIELD, OPERATOR, VALUE)
    # @param rel_filters list : list of tuples formatted as (('superior'|'subordinate', FIELD), OPERATOR, VALUE)
    # @param data dict
    # @return bool
    # @todo prendre en compte les rel_filters
    def update(self, letype, leclass, filters, rel_filters, data):

        query_table_name = self.datasource_utils.get_table_name_from_class(leclass.__name__)
        where_filters = filters
        set_data = data

        prepared_rel_filters = self._prepare_rel_filters(rel_filters)

        # Building the query
        query = update(table=query_table_name, where=where_filters, set=set_data)
        # Executing the query
        with self.connection as cur:
            cur.execute(query)
        return True

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

    ## @brief Link two object given a relation nature, depth and rank
    # @param lesup LeObject : a LeObject
    # @param lesub LeObject : a LeObject
    # @param nature str|None : The relation nature or None if rel2type
    # @param rank int : a rank
    def add_relation(self, lesup, lesub, nature=None, depth=None, rank=None, **rel_attr):
        if len(rel_attr) > 0 and nature is not None:
            #not a rel2type but have some relation attribute
            raise AttributeError("No relation attributes allowed for non rel2type relations")

        with self.connection() as cur:
            sql = insert(self.datasource_utils.relations_table_name, {'id_sup': lesup.lodel_id, 'id_sub': lesub.lodel_id, 'nature': nature, 'rank': rank, 'depth': depth})
            if cur.execute(sql) != 1:
                raise RuntimeError("Unknow SQL error")

            if len(rel_attr) > 0:
                #a relation table exists
                cur.execute('SELECT last_insert_id()')
                relation_id, = cur.fetchone()
                raise NotImplementedError()

        return True

    ## @brief Delete a link between two objects given a relation nature
    # @param lesup LeObject : a LeObject
    # @param lesub LeObject : a LeObject
    # @param nature str|None : The relation nature
    def del_relation(self, lesup, lesub, nature=None):
        raise NotImplementedError()

    ## @brief Return all relation of a lodel_id given a position and a nature
    # @param lodel_id int : We want the relations of this lodel_id
    # @param superior bool : If true search the relations where lodel_id is in id_sup
    # @param nature str|None : Search for relations with the given nature (if None rel2type)
    # @param return an array of dict with keys [ id_sup, id_sub, rank, depth, nature ]
    def get_relations(self, lodel_id, superior=True, nature=None):
        raise NotImplementedError()
