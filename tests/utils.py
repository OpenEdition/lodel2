from plugins.mongodb_datasource.utils import connection


def datasource_tests_init(conn_args):
    conn = connection(host=conn_args['host'],
                      port=conn_args['port'],
                      username=conn_args['username'],
                      password=conn_args['password'])
    database = conn[conn_args['db_name']]
    return (conn, database)


def datasource_tests_db_clean(conn, dbname):
    conn.drop_database(dbname)
