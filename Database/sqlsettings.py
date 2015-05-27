# -*- coding: utf-8 -*-

class SQLSettings(object):
    
    DEFAULT_HOSTNAME = 'localhost'
        
    dbms_list = {
        'postgresql': {
            'driver': 'psycopg2',
            'encoding': 'utf8',
        },
        'mysql': {
            # TODO à définir
            'driver': 'pymysql',
            'encoding': 'utf8',
        }
    }

    DB_READ_CONNECTION_NAME = 'default'  # TODO A configurer
    DB_WRITE_CONNECTION_NAME = 'default'  # TODO A configurer
    
    querystrings = {
        'add_column': {
            'default': 'ALTER TABLE %s ADD COLUMN %s %s'
        },
        'alter_column': {
            'postgresql': 'ALTER TABLE %s ALTER COLUMN %s TYPE %s',
            'mysql': 'ALTER TABLE %s ALTER COLUMN %s %s'
        },
        'drop_column': {
            'default': 'ALTER TABLE %s DROP COLUMN %s'
        }
    }
    
    ACTION_TYPE_WRITE = 'write'
    ACTION_TYPE_READ = 'read'
