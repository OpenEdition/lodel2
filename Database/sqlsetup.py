# -*- coding: utf-8 -*-

from Database.sqlwrapper import SqlWrapper
import sqlalchemy as sql

class SQLSetup(object): 

    def initDb(self, dbconfname = 'default', alchemy_logs=None):
        db = SqlWrapper(read_db = dbconfname, write_db = dbconfname, alchemy_logs=alchemy_logs)
        tables = self.get_schema()
        db.dropAll()
        db.createAllFromConf(tables)

    def get_schema(self):
        tables = []

        default_columns = [
            {"name":"uid",          "type":"INTEGER", "extra":{"foreignkey":"uids.uid", "nullable":False, "primarykey":True}},
            {"name":"name",         "type":"VARCHAR(50)", "extra":{"nullable":False, "unique":True}},
            {"name":"string",       "type":"TEXT"},
            {"name":"help",         "type":"TEXT"},
            {"name":"rank",         "type":"INTEGER"},
            {"name":"date_create",  "type":"DATETIME"},
            {"name":"date_update",  "type":"DATETIME"},
        ]

        # Table listing all objects created by lodel, giving them an unique id
        uids = {
                "name":"uids",
                "columns":[
                    {"name":"uid",          "type":"INTEGER", "extra":{"nullable":False, "primarykey":True, 'autoincrement':True}},
                    {"name":"table",        "type":"VARCHAR(50)"}
                ]
            }
        tables.append(uids)


        # Table listing the classes
        em_class = {"name":"em_class"}
        em_class['columns'] = default_columns + [
            {"name":"classtype",    "type":"VARCHAR(50)"},
            {"name":"sortcolumn",   "type":"VARCHAR(50)", "extra":{"default":"rank"}},
            {"name":"icon",         "type":"INTEGER"},
        ]
        tables.append(em_class)


        # Table listing the types
        em_type = {"name":"em_type"}
        em_type['columns'] = default_columns + [
            {"name":"class_id",     "type":"INTEGER", "extra":{"foreignkey":"em_class.uid", "nullable":False}},
            {"name":"sortcolumn",   "type":"VARCHAR(50)", "extra":{"default":"rank"}},
            {"name":"icon",         "type":"INTEGER"},
        ]
        tables.append(em_type)

        # relation between types: which type can be a child of another
        em_type_hierarchy = {"name":"em_type_hierarchy"}
        em_type_hierarchy['columns'] = [
            {"name":"superior_id",    "type":"INTEGER", "extra":{"foreignkey":"em_type.uid", "nullable":False, "primarykey":True}},
            {"name":"subordinate_id", "type":"INTEGER", "extra":{"foreignkey":"em_type.uid", "nullable":False, "primarykey":True}},
            {"name":"nature",         "type":"VARCHAR(50)", "extra":{"primarykey":True}},
        ]
        tables.append(em_type_hierarchy)

       # Table listing the fieldgroups of a class
        em_fieldgroup = {"name":"em_fieldgroup"}
        em_fieldgroup['columns'] = default_columns + [
            {"name":"class_id",     "type":"INTEGER", "extra":{"foreignkey":"em_class.uid", "nullable":False}},
        ]
        tables.append(em_fieldgroup)

        # Table listing the fields of a fieldgroup
        em_field = {"name":"em_field"}
        em_field['columns'] = default_columns + [
            {"name":"fieldtype",   "type":"VARCHAR(50)", "extra":{"nullable":False}},
            {"name":"fieldtype_opt", "type":"VARCHAR(512)", "nullable": False},
            {"name":"fieldgroup_id",  "type":"INTEGER", "extra":{"foreignkey":"em_fieldgroup.uid", "nullable":False}},
            {"name":"rel_to_type_id", "type":"INTEGER", "extra":{"foreignkey":"em_type.uid", "nullable":True, "server_default": sql.text('NULL')}}, # if relational: type this field refer to
            {"name":"rel_field_id",   "type":"INTEGER", "extra":{"foreignkey":"em_type.uid", "nullable":True, "server_default": sql.text('NULL')}}, # if relational: field that specify the rel_to_type_id
            {"name":"optional",       "type":"BOOLEAN"},
            {"name":"internal",       "type":"BOOLEAN"},
            {"name":"icon",           "type":"INTEGER"},
        ]
        tables.append(em_field)

        # selected field for each type
        em_field_type = {"name":"em_field_type"}
        em_field_type['columns'] = [
            {"name":"type_id",   "type":"INTEGER", "extra":{"foreignkey":"em_type.uid", "nullable":False, "primarykey":True}},
            {"name":"field_id",  "type":"INTEGER", "extra":{"foreignkey":"em_field.uid", "nullable":False, "primarykey":True}},
        ]
        tables.append(em_field_type)

        # Table of the objects created by the user (instance of the types)
        objects = {
            "name":"objects",
            "columns":[
                {"name":"uid",         "type":"INTEGER", "extra":{"foreignkey":"uids.uid", "nullable":False, "primarykey":True}},
                {"name":"string",      "type":"VARCHAR(50)"},
                {"name":"class_id",    "type":"INTEGER", "extra":{"foreignkey":"em_class.uid"}},
                {"name":"type_id",     "type":"INTEGER", "extra":{"foreignkey":"em_type.uid"}},
                {"name":"date_create", "type":"DATETIME"},
                {"name":"date_update", "type":"DATETIME"},
                {"name":"history",     "type":"TEXT"}
            ]
        }
        tables.append(objects)

        # Table listing all files
        # TODO Préciser les colonnes à ajouter
        files = {
            "name":"files",
            "columns":[
                {"name":"uid",     "type":"INTEGER", "extra":{"foreignkey":"uids.uid", "nullable":False, "primarykey":True}},
                {"name":"field1",  "type":"VARCHAR(50)"}
            ]
        }
        tables.append(files)

        return tables
