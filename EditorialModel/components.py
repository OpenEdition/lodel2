# -*- coding: utf-8 -*-

""" Main object to manipulate Editorial Model
    parent of all other EM editing classes
    @see EmClass, EmType, EmFieldGroup, EmField
"""

from Lodel.utils.mlstring import MlString
#from Database.sqlwrapper import SqlWrapper
import logging
import sqlalchemy as sql
from Database import sqlutils

logger = logging.getLogger('Lodel2.EditorialModel')

class EmComponent(object):

    dbconf = 'default' #the name of the engine configuration

    """ instaciate an EmComponent
        @param id_or_name int|str: name or id of the object
        @exception TypeError
    """
    def __init__(self, id_or_name):
        if self is EmComponent:
            raise EnvironmentError('Abstract class')
        if isinstance(id_or_name, int):
            self.id = id_or_name
            self.name = None
        elif isinstance(id_or_name, str):
            self.id = None
            self.name = id_or_name
            self.populate()
        else:
            raise TypeError('Bad argument: expecting <int> or <str>')

    """ Lookup in the database properties of the object to populate the properties
    """
    def populate(self):
        records = self._populateDb() #Db query

        for record in records:
            row = type('row', (object,), {})()
            for k in record.keys():
                setattr(row, k, record[k])

        self.id = int(row.uid)
        self.name = row.name
        self.rank = 0 if row.rank is None else int(row.rank)
        self.date_update = row.date_update
        self.date_create = row.date_create
        self.string = MlString.load(row.string)
        self.help = MlString.load(row.help)

        return row

    @classmethod
    def getDbE(c):
        """ Shortcut that return the sqlAlchemy engine """
        return sqlutils.getEngine(c.dbconf)

    def _populateDb(self):
        """ Do the query on the db """
        dbe = self.__class__.getDbE()
        component = sql.Table(self.table, sqlutils.meta(dbe))
        req = sql.sql.select([component])

        if self.id == None:
            req.where(component.c.name == self.name)
        else:
            req.where(component.c.uid == self.id)
        c = dbe.connect()
        res = c.execute(req)
        c.close()

        res = res.fetchall()

        if not res or len(res) == 0:
            raise EmComponentNotExistError("No component found with "+('name '+self.name if self.id == None else 'id '+self.id ))

        return res

    """ write the representation of the component in the database
        @return bool
    """
    def save(self, values):
        values['name'] = self.name
        values['rank'] = self.rank
        values['date_update'] = self.date_update
        values['date_create'] = self.date_create
        values['string'] = str(self.string)
        values['help']= str(self.help)

        self._saveDb(values)

    def _saveDb(self, values):
        """ Do the query on the db """
        dbe = self.__class__.getDbE()
        component = sql.Table(self.table, sqlutils.meta(dbe))
        req = sql.update(t, values = values).where(component.id == self.id)

        c = dbe.connect()
        res = c.execute(req)
        c.close()
        if not res:
            raise RuntimeError("Unable to save the component in the database")
        

    """ delete this component data in the database
        @return bool
    """
    def delete(self):
        #<SQL>
        dbe = self.__class__.getDbE()
        component = sql.Table(self.table, sqlutils.meta(dbe))
        req= component.delete().where(component.id == self.id)
        c = dbe.connect()
        res = c.execute(req)
        c.close
        if not res:
            raise RuntimeError("Unable to delete the component in the database")
        #</SQL>
        pass

    """ change the rank of the component
        @param int new_rank new position
    """
    def modify_rank(self, new_rank):
        pass

    def __repr__(self):
        if self.name is None:
            return "<%s #%s, 'non populated'>" % (type(self).__name__, self.id)
        else:
            return "<%s #%s, '%s'>" % (type(self).__name__, self.id, self.name)


class EmComponentNotExistError(Exception):
    pass
