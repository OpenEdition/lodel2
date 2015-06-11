# -*- coding: utf-8 -*-

import os

import sqlalchemy as sqla
from sqlalchemy.ext.compiler import compiles

## @file sqlalter.py
# This file defines all DDL (data definition langage) for the ALTER TABLE instructions
# 
# It uses the SqlAlchemy compilation and quoting methos to generate SQL


class AddColumn(sqla.schema.DDLElement):
    """ Defines the ddl for adding a column to a table """
    def __init__(self,table, column):
        """ Instanciate the DDL
            @param table sqlalchemy.Table: A sqlalchemy table object
            @param column sqlalchemy.Column: A sqlalchemy column object
        """
        self.col = column
        self.table = table

@compiles(AddColumn, 'mysql')
@compiles(AddColumn, 'postgresql')
@compiles(AddColumn, 'sqlite')
def visit_add_column(element, ddlcompiler, **kw):
    """ Compiles the AddColumn DDL for mysql, postgresql and sqlite"""
    prep = ddlcompiler.sql_compiler.preparer
    tname = prep.format_table(element.table)
    colname = prep.format_column(element.col)
    return 'ALTER TABLE %s ADD COLUMN %s %s'%(tname,  colname, element.col.type)

@compiles(AddColumn)
def visit_add_column(element, ddlcompiler, **kw):
    raise NotImplementedError('Add column not yet implemented for '+str(ddlcompiler.dialect.name))

class DropColumn(sqla.schema.DDLElement):
    """ Defines the DDL for droping a column from a table """
    def __init__(self, table, column):
        """ Instanciate the DDL
            @param table sqlalchemy.Table: A sqlalchemy table object
            @param column sqlalchemy.Column: A sqlalchemy column object representing the column to drop
        """
        self.col = column
        self.table = table

@compiles(DropColumn,'mysql')
@compiles(DropColumn, 'postgresql')
def visit_drop_column(element, ddlcompiler, **kw):
    """ Compiles the DropColumn DDL for mysql & postgresql """
    prep = ddlcompiler.sql_compiler.preparer
    tname = prep.format_table(element.table)
    colname = prep.format_column(element.col)
    return 'ALTER TABLE %s DROP COLUMN %s'%(tname, colname)

@compiles(DropColumn)
def visit_drop_column(element, ddlcompiler, **kw):
    raise NotImplementedError('Drop column not yet implemented for '+str(ddlcompiler.dialect.name))

class AlterColumn(sqla.schema.DDLElement):
    """ Defines the DDL for changing the type of a column """
    def __init__(self, table, column):
        """ Instanciate the DDL
            @param table sqlalchemy.Table: A sqlalchemy Table object
            @param column sqlalchemy.Column: A sqlalchemy Column object representing the new column
        """
        self.col = column
        self.table = table

@compiles(AlterColumn, 'mysql')
def visit_alter_column(element, ddlcompiler, **kw):
    """ Compiles the AlterColumn DDL for mysql """
    prep = ddlcompiler.sql_compiler.preparer
    tname = prep.format_table(element.table)
    colname = prep.format_column(element.col)
    return 'ALTER TABLE %s ALTER COLUMN %s %s'%(tname, colname, element.col.type)

@compiles(AlterColumn, 'postgresql')
def visit_alter_column(element, ddlcompiler, **kw):
    """ Compiles the AlterColumn DDL for postgresql """
    prep = ddlcompiler.sql_compiler.preparer
    tname = prep.format_table(element.table)
    colname = prep.format_column(element.col)
    return 'ALTER TABLE %s ALTER COLUMN %s TYPE %s'%(tname, colname, element.col.type)

@compiles(AlterColumn)
def visit_alter_column(element, ddlcompiler, **kw):
    raise NotImplementedError('Alter column not yet implemented for '+str(ddlcompiler.dialect.name))

