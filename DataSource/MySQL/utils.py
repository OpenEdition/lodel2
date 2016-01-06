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
    return "%s%s"%(table_preffix['object'], class_name).lower()

## @brief Return a table name given a class name and a type name
# @param class_name str : The (Em|Le)Class name
# @param type_name str : The (Em|Le)Type name
# @return a table name
def r2t_table_name(class_name, type_name):
    return "%s%s_%s"%(table_preffix['relation'], class_name, type_name).lower()

## @brief Return a column name given a field name
# @param field_name : The EmField or LeObject field name
# @return A column name
def column_name(field_name):
    return field_name.lower();

## @brief gets the fk name between two tables
# @param src_table_name str
# @param dst_table_name str
# @return str
def get_fk_name(cls, src_table_name, dst_table_name):
    return "fk_%s_%s" % (src_table_name, dst_table_name)

def common_table_name(relation=True):
    return common_tables['relation' if relation else 'object']

## @brief Exec a query
# @param query str : SQL query
def query(connection, query):
    with connection as cur:
        try:
            cur.execute(query)
        except Exception as err:
            raise err
        return cur

## @brief Identifier escaping
# @param idname str : An SQL identifier
def escape_idname(cls, idname):
    if '`' in idname:
        raise ValueError("Invalid name : '%s'" % idname)
    return '`%s`' % idname

## @brief Given a fieldtype, returns a MySQL type specifier
# @param emfieldType EmFieldType : A fieldtype
# @return str
def get_type_spec_from_fieldtype(cls, emfieldtype):

    ftype = emfieldtype.ftype

    if ftype == 'char' or ftype == 'str':
        res = "VARCHAR(%d)" % emfieldtype.max_length
    elif ftype == 'text':
        res = 'TEXT'
    elif ftype == 'datetime':
        res = "DATETIME"
        # client side workaround for only one column with CURRENT_TIMESTAMP : giving NULL to timestamp that don't allows NULL
        # cf. https://dev.mysql.com/doc/refman/5.0/en/timestamp-initialization.html#idm139961275230400
        # The solution for the migration handler is to create triggers :
        # CREATE TRIGGER trigger_name BEFORE INSERT ON `my_super_table`
        # FOR EACH ROW SET NEW.my_date_column = NOW();
        # and
        # CREATE TRIGGER trigger_name BEFORE UPDATE ON
    elif ftype == 'bool':
        res = "BOOL"
    elif ftype == 'int':
        res = "INT"
    elif ftype == 'rel2type':
        res = "INT"
    else:
        raise ValueError("Unsupported fieldtype ftype : %s" % ftype)

    return res

## Brief add table prefix to a column name
# @param name string: column name to prefix
# @param prefixes dict(prefix:list(name,))
# @return prefixed_name string: the name prefixed
# find the same name in some list of names, prepend the key of the dict to the name
def find_prefix(name, prefixes):
    for prefix, names in prefixes:
        if name in names:
            return MySQL.column_prefix(prefix, name)
    return name

## prefix a column name with the table name
def column_prefix(table, column):
    return '%s.%s' % (table, column)
