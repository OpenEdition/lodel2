# -*- coding: utf-8 -*-

from sql_settings import SqlSettings as sqlsettings
from sqlmanager import SQLManager

class SQLSetup(object): 

    def initDb(self):
        
        sqlmanager = SQLManager()
        
        tables = []

        # Table em_object
        tables.append(
            {
                "name":"em_object",
                "columns":[
                    {"name":"id_global","type":"VARCHAR(50)", "extra":{"nullable":False,"unique":True}},
                    {"name":"type","type":"VARCHAR(50)"}
                ]
            }
        )

        # Table em_document
        tables.append(
            {
                "name":"em_document",
                "columns":[
                    {"name":"id_global","type":"VARCHAR(50)","extra":{"nullable":False,"unique":True}}, # TODO Foreign Key ?
                    {"name":"string","type":"VARCHAR(50)"},
                    {"name":"slug","type":"VARCHAR(50)"},
                    {"name":"id_class","type":"VARCHAR(50)", "extra":{"foreignkey":"em_class.id_global"}},
                    {"name":"id_type","type":"VARCHAR(50)", "extra":{"foreignkey":"em_type.id_global"}},
                    {"name":"status","type":"VARCHAR(50)"},
                    {"name":"date_update","type":"DATE"},
                    {"name":"date_create","type":"DATE"},
                    {"name":"history","type":"TEXT"}
                ]
            }
        )

        # Table em_file
        # TODO Préciser les colonnes à ajouter
        tables.append(
            {
                "name":"em_file",
                "columns":[
                    {"name":"id_global","type":"VARCHAR(50)","extra":{"nullable":False,"unique":True}}, # TODO Foreign Key ?
                    {"name":"field1","type":"VARCHAR(50)"}
                ]
            }
        )

        # Table em_class
        tables.append(      
            {
                "name":"em_class",
                "columns":[
                    {"name":"id_global","type":"VARCHAR(50)","extra": {"nullable":False, "unique":True}},
                    {"name":"name","type":"VARCHAR(50)", "extra":{"nullable":False, "unique":True}},
                    {"name":"classtype","type":"INTEGER"},
                    {"name":"sortcolumn","type":"VARCHAR(50)", "extra":{"default":"rank"}},
                    {"name":"string","type":"TEXT", "extra":{"default":"name"}},
                    {"name":"help", "type":"TEXT"},
                    {"name":"icon", "type":"VARCHAR(50)"},
                    {"name":"rank", "type":"INTEGER"},
                    {"name":"date_update", "type":"DATE"},
                    {"name":"date_create", "type":"DATE"}
                ]
            }
        )

        # Table em_type
        tables.append(
            {
                "name":"em_type",
                "columns":[
                    {"name":"globalid","type":"VARCHAR(50)","extra":{"nullable":False, "unique":True}},
                    {"name":"id_class","type":"VARCHAR(50)","extra":{"nullable":False, "primarykey":True, "foreignkey":"em_class.id_global"}},
                    {"name":"name","type":"VARCHAR(50)","extra":{"nullable":False, "primarykey":True}},
                    {"name":"string", "type": "TEXT","extra":{"default":"name"}},
                    {"name":"help", "type": "TEXT"},
                    {"name":"sortcolumn","type":"VARCHAR(50)", "extra":{"default":"rank"}},
                    {"name":"icon","type":"VARCHAR(50)"},
                    {"name":"rank","type":"INTEGER"},
                    {"name":"date_update","type":"DATE"},
                    {"name":"date_create","type":"DATE"}
                ]
            }
        )

        # Table em_fieldgroup
        tables.append(
            {
                "name":"em_fieldgroup",
                "columns":[
                    {"name":"globalid","type":"VARCHAR(50)","extra":{"nullable":False, "unique":True}},
                    {"name":"id_class","type":"VARCHAR(50)","extra":{"nullable":False, "primarykey":True, "foreignkey":"em_class.id_global"}},
                    {"name":"name","type":"VARCHAR(50)","extra":{"nullable":False, "primarykey":True}},
                    {"name":"string","type":"TEXT","extra":{"default":"name"}},
                    {"name":"help", "type":"TEXT"},
                    {"name":"rank","type":"INTEGER"},
                    {"name":"date_update","type":"DATE"},
                    {"name":"date_create","type":"DATE"}
                ]
            }
        )

        # Table em_field
        tables.append(
            {
                "name":"em_field",
                "columns":[
                    {"name":"globalid","type":"VARCHAR(50)","extra":{"nullable":False,"unique":True}},
                    {"name":"id_fieldgroup","type":"VARCHAR(50)","extra":{"nullable":False,"foreignkey":"em_fieldgroup.globalid"}},
                    {"name":"id_type","type":"VARCHAR(50)","extra":{"nullable":False,"foreignkey":"em_type.id_globalid"}},
                    {"name":"name", "type":"VARCHAR(50)", "extra":{"nullable":False,"unique":True}},
                    {"name":"id_fieldtype","type":"VARCHAR(50)","extra":{"nullable":False, "foreignkey":"em_type.globalid"}},
                    {"name":"string","type":"TEXT", "extra":{"default":"name"}},
                    {"name":"help","type":"TEXT"},
                    {"name":"rank","type":"INTEGER"},
                    {"name":"date_update","type":"DATE"},
                    {"name":"date_create","type":"DATE"},
                    {"name":"date_optional","type":"BOOLEAN"},
                    {"name":"id_relation_field","type":"INTEGER",{"nullable":False}}, #TODO Foreign key ?
                    {"name":"internal", "type":"BOOLEAN"},
                    {"name":"defaultvalue","type":"VARCHAR(50)"},
                    {"name":"params","type":"VARCHAR(50)"},
                    {"name":"value","type":"VARCHAR(50)"}
                ]  
            }
        )
        
        return sqlmanager.create_table(tables)
