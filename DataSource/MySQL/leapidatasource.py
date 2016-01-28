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
from EditorialModel.fieldtypes.generic import MultiValueFieldType

from Lodel.settings import Settings
from .fieldtypes import fieldtype_cast

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
        mandatory_fields = []
        class_table = False

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
            class_fk = main_class.uidname()
            main_lodel_id = utils.column_prefix(main_table, main_class.uidname())
            class_lodel_id = utils.column_prefix(class_table, main_class.uidname())
            # do the join
            joins = [left_join(class_table, {main_lodel_id:class_lodel_id})]

            mandatory_fields = [class_fk, 'type_id']

            fields = [(main_table, target_cls.name2class('LeObject').fieldlist()), (class_table, main_class.fieldlist())]

        elif target_cls.is_lehierarch():
            main_table = utils.common_tables['relation']
            fields = [(main_table, target_cls.name2class('LeRelation').fieldlist())]
        elif target_cls.is_lerel2type():
            # find main table
            main_table = utils.common_tables['relation']
            # find relational table
            class_table = utils.r2t_table_name(target_cls._superior_cls.__name__, target_cls._subordinate_cls.__name__)
            class_fk = target_cls.name2class('LeRelation').uidname()
            main_relation_id = utils.column_prefix(main_table, class_fk)
            class_relation_id = utils.column_prefix(class_table, class_fk)
            # do the joins
            lodel_id = target_cls.name2class('LeObject').uidname()
            joins = [
                left_join(class_table, {main_relation_id:class_relation_id}),
                # join with the object table to retrieve class and type of superior and subordinate
                left_join(utils.common_tables['object'] + ' as sup_obj', {'sup_obj.'+lodel_id:target_cls._superior_field_name}),
                left_join(utils.common_tables['object'] + ' as sub_obj', {'sub_obj.'+lodel_id:target_cls._subordinate_field_name})
            ]

            mandatory_fields = [class_fk, 'class_id', 'type_id']

            fields = [
                (main_table, target_cls.name2class('LeRelation').fieldlist()),
                (class_table, target_cls.fieldlist()),
                ('sup_obj', ['class_id']),
                ('sub_obj', ['type_id'])
            ]

        else:
            raise AttributeError("Target class '%s' in get() is not a Lodel Editorial Object !" % target_cls)


        # extract mutltivalued field from field_list
        if class_table:
            multivalue_fields = self.get_multivalue_fields(target_cls)
            for field_names in multivalue_fields.values():
                for field_name in field_names:
                    try:
                        field_list.remove(field_name)
                    except ValueError:
                        pass  # field_name is not in field_list
        else:
            multivalue_fields = False

        # add mandatory fields to field_list
        for mandatory_field in mandatory_fields:
            if mandatory_field not in field_list:
                field_list.append(mandatory_field)

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
        # TODO: this will not work with special filters
        wheres = {(utils.find_prefix(name, fields), op):fieldtype_cast(target_cls.fieldtypes()[name], value) for name,op,value in filters}
        query = select(main_table, select=prefixed_field_list, where=wheres, joins=joins, **kwargs)

        # Executing the query
        cur = utils.query(self.connection, query)
        results = all_to_dicts(cur)
        #print(results)

        # query multivalued tables, inject result in main result
        if multivalue_fields:
            for result in results:
                for key_name, fields in multivalue_fields.items():
                    query_fields = [key_name]
                    query_fields.extend(fields)
                    table_name = utils.multivalue_table_name(class_table, key_name)
                    sql = select(table_name, select=query_fields, where={(class_fk, '='):result[class_fk]})

                    multi = {name:{} for name in fields}
                    cur = utils.query(self.connection, sql)

                    multi_results = all_to_dicts(cur)
                    for multi_result in multi_results:
                        for field in fields:
                            multi[field][multi_result[key_name]] = multi_result[field]
                    result.update(multi)

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

    ## @brief update ONE existing lodel editorial component
    # @param target_cls LeCrud(class) : Instance of the object concerned by the update
    # @param lodel_id : id of the component
    # @param rel_filters list : List of relationnal filters (see @ref leobject_filters)
    # @param **datas : Datas in kwargs
    # @return the number of updated components
    # @todo implement other filters than lodel_id
    def update(self, target_cls, lodel_id, **datas):

        # it is a LeType
        if target_cls.is_letype():
            # find main table and main table datas
            main_table = utils.common_tables['object']
            fk_name = target_cls.uidname()
            main_datas = {fk_name: raw(fk_name)} #  be sure to have one SET clause
            main_fields = target_cls.name2class('LeObject').fieldlist()
            class_table = utils.object_table_name(target_cls.leo_class().__name__)
        elif target_cls.is_lerel2type():
            main_table = utils.common_tables['relation']
            le_relation = target_cls.name2class('LeRelation')
            fk_name = le_relation.uidname()
            main_datas = {fk_name: raw(fk_name)} #  be sure to have one SET clause
            main_fields = le_relation.fieldlist()

            class_table = utils.r2t_table_name(target_cls._superior_cls.__name__, target_cls._subordinate_cls.__name__)
        else:
            raise AttributeError("'%s' is not a LeType nor a LeRelation, it's impossible to update it" % target_cls)


        datas = { fname: fieldtype_cast(target_cls.fieldtypes()[fname], datas[fname]) for fname in datas }

        for main_column_name in main_fields:
            if main_column_name in datas:
                main_datas[main_column_name] = datas[main_column_name]
                del(datas[main_column_name])

        # extract multivalued field from class_table datas
        multivalued_datas = self.create_multivalued_datas(target_cls, datas)

        where = {fk_name: lodel_id}
        sql = update(main_table, where, main_datas)
        utils.query(self.connection, sql)

        # update on class table
        if datas:
            sql = update(class_table, where, datas)
            utils.query(self.connection, sql)

        # do multivalued insert
        # first delete old values, then insert new ones
        for key_name, lines in multivalued_datas.items():
            table_name = utils.multivalue_table_name(class_table, key_name)
            sql = delete(table_name, where)
            utils.query(self.connection, sql)
            for key_value, line_datas in lines.items():
                line_datas[key_name] = key_value
                line_datas[fk_name] = lodel_id
                sql = insert(table_name, line_datas)
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

        # cast datas
        datas = { fname: fieldtype_cast(target_cls.fieldtypes()[fname], datas[fname]) for fname in datas }

        # extract main table datas from datas
        for main_column_name in main_fields:
            if main_column_name in datas:
                if main_column_name not in main_datas:
                    main_datas[main_column_name] = datas[main_column_name]
                del(datas[main_column_name])

        # extract multivalued field from class_table datas
        if class_table:
            multivalued_datas = self.create_multivalued_datas(target_cls, datas)

        sql = insert(main_table, main_datas)
        cur = utils.query(self.connection, sql)
        lodel_id = cur.lastrowid

        if class_table:
            # insert in class_table
            datas[fk_name] = lodel_id
            sql = insert(class_table, datas)
            utils.query(self.connection, sql)

            # do multivalued inserts
            for key_name, lines in multivalued_datas.items():
                table_name = utils.multivalue_table_name(class_table, key_name)
                for key_value, line_datas in lines.items():
                    line_datas[key_name] = key_value
                    line_datas[fk_name] = lodel_id
                    sql = insert(table_name, line_datas)
                    utils.query(self.connection, sql)

        return lodel_id

    # extract multivalued field from datas, prepare multivalued data list
    def create_multivalued_datas(self, target_cls, datas):
            multivalue_fields = self.get_multivalue_fields(target_cls)

            if multivalue_fields:
                # construct multivalued datas
                multivalued_datas = {key:{} for key in multivalue_fields}
                for key_name, names in multivalue_fields.items():
                    for field_name in names:
                        try:
                            for key, value in datas[field_name].items():
                                if key not in multivalued_datas[key_name]:
                                    multivalued_datas[key_name][key] = {}
                                multivalued_datas[key_name][key][field_name] = value
                            del(datas[field_name])
                        except KeyError:
                            pass  # field_name is not in datas
                return multivalued_datas
            else:
                return {}

    # return multivalue fields of a class
    def get_multivalue_fields(self, target_cls):
        multivalue_fields = {}
        # scan fieldtypes to get mutltivalued field
        for field_name, fieldtype in target_cls.fieldtypes(complete=False).items():
                if isinstance(fieldtype, MultiValueFieldType):
                    if  fieldtype.keyname in multivalue_fields:
                        multivalue_fields[fieldtype.keyname].append(field_name)
                    else:
                        multivalue_fields[fieldtype.keyname] = [field_name]

        return multivalue_fields


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
