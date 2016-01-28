# -*- coding: utf8 -*-

from Lodel.settings import Settings

common_tables = {
    'relation': 'relation',
    'object': 'object'
}
table_preffix = {
    'relation': 'rel_',
    'object': 'class_',
}

## @brief indicates if we want ON DELETE CASCADE on foreign keys
# @todo implementation in migration handler
fk_on_delete_cascade = False
## @brief Lodel_id for the hierachy root
leroot_lodel_id = 0


## @brief Return a table name given a EmClass or LeClass name
# @param class_name str : The class name
# @return a table name
def object_table_name(class_name):
    return ("%s%s" % (table_preffix['object'], class_name)).lower()


## @brief Return a table name given a class name and a type name
# @param class_name str : The (Em|Le)Class name
# @param type_name str : The (Em|Le)Type name
# @return a table name
def r2t_table_name(class_name, type_name):
    return ("%s%s_%s" % (table_preffix['relation'], class_name, type_name)).lower()

def multivalue_table_name(referenced_table_name, key_name):
    return ("%s%s" % (key_name, referenced_table_name))

## @brief Return a column name given a field name
# @param field_name : The EmField or LeObject field name
# @return A column name
def column_name(field_name):
    return field_name.lower()


## @brief gets the fk name between two tables
# @param src_table_name str
# @param dst_table_name str
# @return str
def get_fk_name(src_table_name, dst_table_name):
    return ("fk_%s_%s" % (src_table_name, dst_table_name)).lower()


## @brief Exec a query
# @param query str : SQL query
def query(connection, query_string):
    if Settings.debug_sql:
        print("SQL : ", query_string)
    with connection as cur:
        try:
            cur.execute(query_string)
        except Exception as err:
            raise err
        return cur


## @brief Identifier escaping
# @param idname str : An SQL identifier
def escape_idname(idname):
    if '`' in idname:
        raise ValueError("Invalid name : '%s'" % idname)
    return '`%s`' % idname


## Brief add table prefix to a column name
# @param name string: column name to prefix
# @param prefixes dict(prefix:list(name,))
# @return prefixed_name string: the name prefixed
# find the same name in some list of names, prepend the key of the dict to the name
def find_prefix(name, prefixes):
    for prefix, names in prefixes:
        if name in names:
            return column_prefix(prefix, name)
    return name


## prefix a column name with the table name
def column_prefix(table, column):
    return '%s.%s' % (table, column)
