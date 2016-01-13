#-*- coding: utf-8 -*-

## @package DataSource.MySQL.fieldtypes 
# 
# Defines usefull function to handle fieldtype in MySQL datasource

import EditorialModel
from EditorialModel import fieldtypes as ed_fieldtypes
import EditorialModel.fieldtypes.generic
from EditorialModel.fieldtypes.generic import SingleValueFieldType, MultiValueFieldType, ReferenceFieldType
import EditorialModel.fieldtypes.integer
import EditorialModel.fieldtypes.char
import EditorialModel.fieldtypes.bool
import EditorialModel.fieldtypes.text
import EditorialModel.fieldtypes.rel2type

## @brief Returns column specs from fieldtype
# @param emfieldtype EmFieldType : An EmFieldType insance
# @todo escape default value
def singlevaluefieldtype_db_init_specs(emfieldtype):
    colspec = ''
    if not emfieldtype.nullable:
        colspec = 'NOT NULL'
    if hasattr(emfieldtype, 'default'):
        colspec += ' DEFAULT '
        if emfieldtype.default is None:
            colspec += 'NULL '
        else:
            colspec += emfieldtype.default  # ESCAPE VALUE HERE !!!!

    if emfieldtype.name == 'pk':
        colspec += ' AUTO_INCREMENT'

    return colspec

## @brief Given a fieldtype return instructions to be executed by the migration handler
#
# The returned value in a tuple of len = 3
#
# The first items gives instruction type. Possible values are :
# - 'column' : add a column
#  - the second tuple item is the SQL type of the new column
#  - the third tuple item is the SQL specs (constraints like default value, nullable, unique , auto_increment etc.)
# - 'table' : add a column in another table and make a fk to the current table
#  - the second tuple item is a tuple(key_name, key_value)
#  - the third tuple item is a tuple(column_type, column_spec)
# @param fieldtype GenericFieldType : A FieldType instance
# @return a tuple (instruction_type, infos)
def fieldtype_db_init(fieldtype):
    if isinstance(fieldtype, EditorialModel.fieldtypes.rel2type.EmFieldType):
        return (None, None, None)
    elif isinstance(fieldtype, SingleValueFieldType):
        res = [ 'column', None, singlevaluefieldtype_db_init_specs(fieldtype) ]
        # We will create a column
        if isinstance(fieldtype, EditorialModel.fieldtypes.integer.EmFieldType):
            res[1] = 'INT'
        elif isinstance(fieldtype, EditorialModel.fieldtypes.char.EmFieldType):
            res[1] = 'VARCHAR(%d)' % fieldtype.max_length
        elif isinstance(fieldtype, EditorialModel.fieldtypes.text.EmFieldType):
            res[1] = 'TEXT'
        elif isinstance(fieldtype, EditorialModel.fieldtypes.bool.EmFieldType):
            res[1] = 'BOOL'
        elif isinstance(fieldtype, EditorialModel.fieldtypes.datetime.EmFieldType):
            res[1] = 'DATETIME'
        elif isinstance(fieldtype, EditorialModel.fieldtypes.generic.ReferenceFieldType):
            res[1] = 'INT'
        else:
            raise RuntimeError("Unsupported fieldtype : ", fieldtype)
        return tuple(res)
    elif isinstance(fieldtype, MultiValueFieldType):
        res = [ 'table', None, None ]
        key_type, _ = fieldtype_db_init(fieldtype.key_fieldtype)
        key_name = fieldtype.keyname
        res[1] = (key_name, key_type)
        res[2] = fieldtype_db_init(fieldtype.value_fieldtype)
    else:
        raise NotImplementedError("Not yet implemented")
            
    

