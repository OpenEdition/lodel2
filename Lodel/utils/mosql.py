# -*- coding: utf-8 -*-

## @package Lodel.utils.mosql
# @brief Helper function to use mosql library
#
# define create_database and drop_database Query to manipulate databases
# define create, drop and alter Query to manipulate tables
# define create_user, delete_user and grant to manipulate user and rights

from mosql.util import Clause, Statement, Query, value, identifier, concat_by_comma, paren, raw

def col_def(cols):
    print("cols", cols)
    ret = []
    for col in cols:
        print("col", col)
        name, definition = col
        ret.append(identifier(name) + ' ' + raw(definition))
    return ret

# chain definitions
column_list = (col_def, concat_by_comma, paren)

# Clauses
create_clause = Clause('create table', alias='create', no_argument=True)
if_not_exists = Clause('if not exists', alias='if_not_exists', no_argument=True, default=True)
table_clause = Clause('table', (identifier, ), alias='table', hidden=True)
character_clause = Clause('CHARACTER SET', (value, ), alias='character')
column_clause = Clause('column', column_list, alias='column', hidden=True)

alter_clause = Clause('alter table', (identifier, ), alias='table')
add_clause = Clause('add column', (col_def, ), alias='column')

# Statements
create_statement = Statement([create_clause, if_not_exists, table_clause, column_clause, character_clause])
alter_add_statement = Statement([alter_clause, add_clause])

# queries
create = Query(create_statement, ('table', 'column', 'if_not_exists'), {'create':True})
alter_add = Query(alter_add_statement, ('table', 'column'))
