# -*- coding: utf-8 -*-

from sqlalchemy import * # TODO ajuster les classes à importer
from Database.sqlsettings import SQLSettings as sqlsettings
from django.conf import settings
import re

import logging as logger #TODO hack to replace the standarts use of logging in django
logger.getLogger().setLevel('DEBUG')

class SqlWrapper(object):

    def __init__(self, log=False):
        """ Instanciate a new SqlWrapper
            @param log bool: If true activate sqlalchemy logger
        """
        # TODO Passer ces deux éléments dans les settings django (au niveau de l'init de l'appli)
        self.read_engine = self.get_engine(sqlsettings.DB_READ_CONNECTION_NAME, log)
        self.write_engine = self.get_engine(sqlsettings.DB_WRITE_CONNECTION_NAME, log)

    def get_engine(self, connection_name, log=False):
        """ Crée un moteur logique sur une base de données

            @param connection_name str: Connection name as defined is django settings
            @param log bool: If true this engine will have logging enabled
            @return Engine
        """

        connection_params = settings.DATABASES[connection_name]

        if 'ENGINE' not in connection_params:
            raise NameError('Missing ENGINE in configuration file')

        if connection_params['ENGINE'] not in sqlsettings.dbms_list:
            raise NameError('Wrong ENGINE "'+connection_params['ENGINE']+'" in configuration files')
        dialect = connection_params['ENGINE']

        if 'driver' not in sqlsettings.dbms_list[dialect]:
            raise NameError('Wrong ENGINE "'+dialect+'" in configuration files')
        driver = sqlsettings.dbms_list[dialect]['driver']

        if 'NAME' not in connection_params:
            raise NameError('Missing database name in configuration files')
        database = connection_params['NAME']

        if 'USER' in connection_params:
            user = connection_params['USER']
            if 'PASSWORD' in connection_params:
                user += ':'+connection_params['PASSWORD']
        else:
            user = ''

        hostname = connection_params['HOST'] if 'HOST' in connection_params else sqlsettings.DEFAULT_HOSTNAME
        port = connection_params['PORT'] if 'PORT' in connection_params else ''
        host = hostname if port=='' else '%s:%s' % (hostname, port)


        if dialect == 'sqlite':
            connection_string = '%s+%s:///%s' % (dialect, driver, database)
        else:
            connection_string = '%s+%s://%s@%s/%s' % (dialect, driver, user, host, database)

        engine = create_engine(connection_string, encoding=sqlsettings.dbms_list[dialect]['encoding'], echo=log)
        return engine

    def get_read_engine(self):
        return self.read_engine

    def get_write_engine(self):
        return self.write_engine

    def execute(self, queries, action_type):
        """ Exécute une série de requêtes en base

            @param queries list: une liste de requêtes
            @param action_type str: le type d'action ( 'read'|'write' )
            @return List. Tableau de résultats sous forme de tuples (requête, résultat)
        """

        db = self.get_write_engine() if action_type==sqlsettings.ACTION_TYPE_WRITE else self.get_read_engine()
        connection = db.connect()
        transaction= connection.begin()
        result = []

        queries = queries if isinstance(queries, list) else [queries]


        try:
            for query in queries:
                result.append((query, connection.execute(query)))
            transaction.commit()
            connection.close()
        except:
            transaction.rollback()
            connection.close()
            result = None
            raise

        return result

    def create_foreign_key_constraint_object(self, localcol, remotecol, constraint_name=None):
        """ Génère une contrainte Clé étrangère

            @param localcol str: Colonne locale
            @param remotecol str: Colonne distante (syntaxe : Table.col)
            @param constraint_name str: Nom de la contrainte (par défaut : fk_localcol_remotecol)

        Returns:
            ForeignKeyConstraint.
        """

        foreignkeyobj = ForeignKeyConstraint([localcol], [remotecol], name=constraint_name)
        return foreignkeyobj

    def create_column_object(self, column_name, column_type, column_extra=None):
        """ Génère un objet colonne

            Exemple de dictionnaire pour column_extra : { "primarykey":True, "nullable":False, "default":"test" ... }
            @param column_name str: Nom de la colonne
            @param column_type str: Type de la colonne
            @param column_extra dict : Objet json contenant les paramètres optionnels comme PRIMARY KEY, NOT NULL, etc ...

            @return Column. La méthode renvoie "None" si l'opération échoue

        """

        # Traitement du type (mapping avec les types SQLAlchemy)
        # TODO créer une méthode qui fait un mapping plus complet
        column = None
        if column_type=='INTEGER':
            column = Column(column_name, INTEGER)
        elif 'VARCHAR' in column_type:
            check_length = re.search(re.compile('VARCHAR\(([\d]+)\)', re.IGNORECASE), column_type)
            column_length = int(check_length.groups()[0]) if check_length else None
            column = Column(column_name, VARCHAR(length=column_length))
        elif column_type=='TEXT':
            column = Column(column_name, TEXT)
        elif column_type=='DATE':
            column = Column(column_name, DATE)
        elif column_type=='BOOLEAN':
            column = Column(column_name, BOOLEAN)

        if column is not None and column_extra:
            if 'nullable' in column_extra:
                column.nullable = column_extra['nullable']
            if 'primarykey' in column_extra:
                column.primary_key = column_extra['primarykey']
            if 'default' in column_extra:
                column.default = ColumnDefault(column_extra['default'])
            if 'foreignkey' in column_extra:
                column.append_foreign_key(ForeignKey(column_extra['foreignkey']))


        return column

    def create_table(self, tableparams):
        """ Crée une nouvelle table

            Les paramètres de la tables sont passés via un dictionnaire dont voici la description :
            { 'name':'<nom_table>', 'columns': [ <col1>, <col2>, <coln> ], 'constraints': dict(...) }
            Avec <colX> : { 'name': '<name_colX>', 'type': '<type_colX>', 'extra': dict(...) }
            A noter que les types de col (<type_colX>) sont des chaines representant un type SQL (ex: "VARCHAR(50)")
            Les deux champs "name" et "columns" seulement sont obligatoires.
            Le champ "extra" de la définition des colonnes est facultatif.

            @args tableparams dict: Dictionnaire avec les paramétrages de la table

            @return bool. True si le process est allé au bout, False si on a rencontré une erreur.

        """

        metadata = MetaData()
        table = Table(tableparams['name'], metadata)
        columns = tableparams['columns']
        for column in columns:
            column_extra = column['extra'] if 'extra' in column else None
            table.append_column(self.create_column_object(column['name'], column['type'], column_extra))

        try:
            table.create(self.get_write_engine())
            return True
        except Exception as e:
            # TODO Ajuster le code d'erreur à retourner
            logger.warning("Error creating table : "+str(e))
            return False


    def get_table(self, table_name, action_type=sqlsettings.ACTION_TYPE_WRITE):
        """ Récupère une table dans un objet Table
            
            @param table_name str: Nom de la table
            @param action_type str: Type d'action (read|write) (par défaut : "write")
            @return Table.
        """
        db = self.get_write_engine() if action_type == sqlsettings.ACTION_TYPE_WRITE else self.get_read_engine()
        metadata = MetaData()

        return Table(table_name, metadata, autoload=True, autoload_with=db)


    def drop_table(self, table_name):
        """ Supprime une table
            @param table_name str: Nom de la table
            @return bool. True si le process est allé au bout. False si on a rencontré une erreur
        """

        try:
            db = self.get_write_engine().connect()
            metadata = MetaData()
            table = Table(table_name, metadata, autoload=True, autoload_with=db)
            # Pour le drop, on utilise checkfirst qui permet de demander la suppression préalable des contraintes liées à la table
            table.drop(db, checkfirst=True)
            db.close()
            return True
        except Exception as e:
            # TODO ajuster le code d'erreur
            logger.warning("Error droping table : "+str(e))
            return False


    def get_querystring(self, action, dialect):
        string_dialect = dialect if dialect in sqlsettings.querystrings[action] else 'default'
        querystring = sqlsettings.querystrings[action][string_dialect]
        return querystring

    def add_column(self, table_name, column):
        """ Ajoute une colonne à une table existante

            @param table_name str: nom de la table
            @param column dict: la colonne - {"name":"<nom de la colonne>", "type":"<type de la colonne>"}

            @return bool. True si le process est allé au bout, False si on a rencontré une erreur
        """

        sqlquery = self.get_querystring('add_column', self.get_write_engine().dialect) % (table_name, column['name'], column['type'])
        sqlresult = self.execute(sqlquery, sqlsettings.ACTION_TYPE_WRITE)
        return True if sqlresult else False

    def alter_column(self, table_name, column):
        """ Modifie le type d'une colonne

            @param table_name str: nom de la table
            @param column_name dict: la colonne - {"name":"<nom de la colonne>","type":"<nouveau type de la colonne>"}

            @return bool. True si le process est allé au bout. False si on a rencontré une erreur
        """

        sqlquery = self.get_querystring('alter_column', self.get_write_engine().dialect) % (table_name, column['name'], column['type'])
        sqlresult = self.execute(sqlquery, sqlsettings.ACTION_TYPE_WRITE)
        return True if sqlresult else False

    def insert(self, table_name, newrecord):
        """ Insère un nouvel enregistrement

            @param table_name str: nom de la table
            @param newrecord dict: dictionnaire contenant les informations sur le nouvel enregistrement à insérer - {"column1":"value1", "column2":"value2", etc ...)

            @return int. Nombre de lignes insérées
        """
        sqlresult = self.execute(self.get_table(table_name).insert().values(newrecord), sqlsettings.ACTION_TYPE_WRITE)
        return sqlresult.rowcount

    def delete(self, table_name, whereclauses):
        """ Supprime un enregistrement

            @param table_name str: nom de la table
            @param whereclauses list: liste des conditions sur les enregistrements (sous forme de textes SQL)

            @return int. Nombre de lignes supprimées
        """

        deleteobject = self.get_table(table_name).delete()

        for whereclause in whereclauses:
            deleteobject = deleteobject.where(whereclause)

        sqlresult = self.execute(deleteobject, sqlsettings.ACTION_TYPE_WRITE)
        return sqlresult.rowcount

    def update(self, table_name, whereclauses, newvalues):
        """ Met à jour des enregistrements

            @param table_name str: nom de la table
            @param whereclauses list: liste des conditions sur les enregistrements (sous forme de textes SQL)
            @param newvalues dict: dictionnaire contenant les nouvelles valeurs à insérer - {"colonne1":"valeur1", "colonne2":"valeur2", etc ...}

            @return int. Nombre de lignes modifiées

            @throw DataError. Incompatibilité entre la valeur insérée et le type de colonne dans la table
        """

        table = self.get_table(table_name)
        update_object = table.update()

        updated_lines_count = 0

        try:
            for whereclause in whereclauses:
                update_object = update_object.where(whereclause)

            update_object = update_object.values(newvalues)

            sqlresult = self.execute(update_object, sqlsettings.ACTION_TYPE_WRITE)
            updated_lines_count = sqlresult.rowcount

        except DataError as e:
            # TODO Voir si on garde "-1" ou si on place un "None" ou un "False"
            logger.warning("Error updating database : "+str(e))
            updated_lines_count = -1

        return updated_lines_count

    def select(self, select_params):
        """ Récupère un jeu d'enregistrements

            Champs de select_params :
            - "what":"<liste des colonnes>",
            - "from":"<liste des tables>",
            - "where":"<liste des conditions>",
            - "distinct":True|False,
            - "join":{"left":"table_de_gauche.champ","right":"table_de_droite.champ", "options":{"outer":True|False}}
            - ...

            Les listes sont supportées sous deux formats :
            - texte SQL : "colonne1, colonne2, ..."
            - liste Python : ["colonne1", "colonne2", ...]

            @param select_params list: liste de dictionnaire permettant de caractériser la requête.

            @return list. Liste des dictionnaires représentant les différents enregistrements.
        """

        if not 'what' in select_params or not 'from' in select_params:
            # TODO Lever une exception à ce niveau
            raise

        query_what = select_params['what'] if isinstance(select_params['what'], list) else select_params['what'].replace(' ', '').split(',')
        query_from = select_params['from'] if isinstance(select_params['from'], list) else select_params['from'].replace(' ', '').split(',')
        query_where= select_params['where'] if isinstance(select_params['where'], list) else select_params['where'].replace(' ', '').split(',')
        query_distinct = select_params['distinct'] if 'distinct' in select_params else False
        query_limit = select_params['limit'] if 'limit' in select_params else False
        query_offset = select_params['offset'] if 'offset' in select_params else False
        query_orderby = select_params['order_by'] if 'order_by' in select_params else False
        query_groupby = select_params['group_by'] if 'group_by' in select_params else False
        query_having = select_params['having'] if 'having' in select_params else False

        columns_list = []
        if len(query_from) > 1:
            for column_id in query_what:
                # Il y a plusieurs tables, les colonnes sont donc nommées sur le format suivant : <nom de la table>.<nom du champ>
                column_id_array = column_id.split('.')
                columns_list.append(getattr(self.get_table(column_id_array[0]).c, column_id_array[1]))
        else:
            table = self.get_table(query_from[0])


        select_object = select(columns=columnslist)

        selected_lines = []

        try:
            # Traitement des différents paramètres de la requête
            for query_where_item in query_where:
                select_object = select_object.where(query_where_item)

            select_object = select_object.distinct(True) if query_distinct else select_object
            select_object = select_object.limit(query_limit) if query_limit else select_object
            select_object = select_object.offset(query_offset) if query_offset else select_object

            if query_orderby:
                for query_orderby_column, query_orderby_direction in query_orderby:
                    select_object = select_object.order_by("%s %s" % (query_orderby_column, query_orderby_direction))

            #Traitement de la jointure
            if 'join' in select_params:
                select_join = self.create_join_object(select_params['join'])
                if select_join:
                    select_object = select_object.select_from(select_join)
                else:
                    raise # TODO Ajuster l'exception à lever (ici :"Données de jointure invalides ou manquantes")

            #Traitement du group_by
            if query_groupby:
                for group_by_clause in query_groupby:
                    select_object = select_object.group_by(self.get_table_column_from_sql_string(group_by_clause))

            # Traitement du having
            if query_groupby and query_having:
                for having_clause in query_having:
                    select_object = select_object.having(having_clause)

            # Exécution de la requête
            sqlresult = self.execute(select_object, sqlsettings.ACTION_TYPE_READ)

            # Transformation du résultat en une liste de dictionnaires
            records = sqlresult.fetchall()
            for record in records:
                selected_lines.append(dict(zip(record.keys(), record)))
        except Exception as e:
            logger.debug("Error selecting in database : "+str(e))
            selected_lines = None

        return selected_lines

    def get_table_column_from_sql_string(self,sql_string):

        sql_string_array = sql_string.split('.')
        table_name = sql_string_array[0]
        column_name = sql_string_array[1]
        table_object = self.get_table(table_name,sqlsettings.ACTION_TYPE_READ)
        column_object = getattr(table_object.c, column_name)

        return column_object


    def create_join_object(self, join_params):
        """Génère un objet "Jointure" pour le greffer dans une requête

            Format des dictionnaires de description des jointures :
            - Format1 liste de champs
             - "left":"table.champ",
             - "right":"table.champ",
             - "options":{"outer":True|False}
            - Format2 liste de champs
             - "left":{"table":"nom de la table","field":"nom du champ"},
             - "right":{"table":"nom de la table","field":"nom du champ"},
             - "options":{"outer":True|False}
    
            @param join_params (dict) : dictionnaire de données sur la jointure.
            @return join.
        """

        join_object = None

        if 'left' in join_params and 'right' in join_params:
            if isinstance(join_params['left'], dict):
                join_left_table_name = join_params['left']['table']
                join_left_field_name = join_params['left']['field']
            else:
                join_left_array = join_params['left'].split('.')
                join_left_table_name = join_left_array[0]
                join_left_field_name = join_left_array[1]

            if isinstance(join_params['right'], dict):
                join_right_table_name = join_params['right']['table']
                join_right_field_name = join_params['right']['field']
            else:
                join_right_array = join_params['right'].split('.')
                join_right_table_name = join_right_array[0]
                join_right_field_name = join_right_array[1]

            left_table = self.get_table(join_left_table_name, sqlsettings.ACTION_TYPE_READ)
            left_field = getattr(left_table.c, join_left_field_name)

            right_table = self.get_table(join_right_table_name, sqlsettings.ACTION_TYPE_READ)
            right_field = getattr(right_table.c, join_right_field_name)

            join_option_isouter = True if 'options' in join_params and 'outer' in join_params and join_params['outer']==True else False

            join_object = join(left_table, right_table, left_field == right_field,isouter=join_option_isouter)

        return join_object
