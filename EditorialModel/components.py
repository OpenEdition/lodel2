# -*- coding: utf-8 -*-

""" Main object to manipulate Editorial Model
    parent of all other EM editing classes
    @see EmClass, EmType, EmFieldGroup, EmField
"""

import datetime

from Lodel.utils.mlstring import MlString
import logging
import sqlalchemy as sql
from Database import sqlutils

logger = logging.getLogger('Lodel2.EditorialModel')

class EmComponent(object):

    dbconf = 'default' #the name of the engine configuration
    table = None
    ranked_in = None
    
    """ instaciate an EmComponent
        @param id_or_name int|str: name or id of the object
        @exception TypeError
    """
    def __init__(self, id_or_name):
        if type(self) is EmComponent:
            raise EnvironmentError('Abstract class')
        if isinstance(id_or_name, int):
            self.id = id_or_name
            self.name = None
        elif isinstance(id_or_name, str):
            self.id = None
            self.name = id_or_name
            self.populate()
        else:
            raise TypeError('Bad argument: expecting <int> or <str> but got : '+str(type(id_or_name)))

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
            req = req.where(component.c.name == self.name)
        else:
            req = req.where(component.c.uid == self.id)
        c = dbe.connect()
        res = c.execute(req)
        c.close()

        res = res.fetchall()

        if not res or len(res) == 0:
            raise EmComponentNotExistError("No component found with "+('name '+self.name if self.id == None else 'id '+self.id ))

        return res
    
    ## Insert a new component in the database
    # This function create and assign a new UID and handle the date_create value
    # @param values The values of the new component
    # @return An instance of the created component
    #
    # @todo Check that the query didn't failed
    @classmethod
    def create(c, values):
        values['uid'] = c.newUid()
        values['date_update'] = values['date_create'] = datetime.datetime.utcnow()

        dbe = c.getDbE()
        conn = dbe.connect()
        table = sql.Table(c.table, sqlutils.meta(dbe))
        req = table.insert(values)
        res = conn.execute(req) #Check res?
        conn.close()
        return c(values['name']) #Maybe no need to check res because this would fail if the query failed
        

    """ write the representation of the component in the database
        @return bool
    """
    def save(self, values):

        values['name'] = self.name
        values['rank'] = self.rank
        values['date_update'] = datetime.datetime.utcnow()
        values['string'] = str(self.string)
        values['help']= str(self.help)

        #Don't allow creation date overwritting
        if 'date_create' in values:
            del values['date_create']
            logger.warning("date_create supplied for save, but overwritting of date_create not allowed, the date will not be changed")

        self._saveDb(values)

    def _saveDb(self, values):
        """ Do the query on the db """
        dbe = self.__class__.getDbE()
        component = sql.Table(self.table, sqlutils.meta(dbe))
        req = sql.update(component, values = values).where(component.c.uid == self.id)

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
        req= component.delete().where(component.c.uid == self.id)
        c = dbe.connect()
        res = c.execute(req)
        c.close
        if not res:
            raise RuntimeError("Unable to delete the component in the database")
        #</SQL>
        pass

    ## modify_rank
    #
    # Permet de changer le rank d'un component, soit en lui donnant un rank précis, soit en augmentant ou reduisant sont rank actuelle d'une valleur donné.
    #
    # @param new_rank int: le rank ou modificateur de rank
    # @param sign str: Un charactère qui peut être : '=' pour afecter un rank, '+' pour ajouter le modificateur de rank ou '-' pour soustraire le modificateur de rank.
    #
    # @return bool: True en cas de réussite False en cas d'echec.
    def modify_rank(self, new_rank, sign):
        if(type(new_rank) is int):
            if(new_rank >= 0):
                dbe = self.__class__.getDbE()
                component = sql.Table(self.table, sqlutils.meta(dbe))
                req = sql.sql.select([component.c.uid, component.c.rank])
                if(sign == '='):
                    req = req.where(getattr(component.c, self.ranked_in) == self.ranked_in and component.c.rank == new_rank)
                    c = dbe.connect()
                    res = c.execute(req)
                    res = res.fetchone()
                    c.close()
                    if(res != None):
                        if(new_rank < self.rank):
                            req = req.where(getattr(component.c, self.ranked_in) == self.ranked_in and (component.c.rank >= new_rank))
                        else:
                            req = req.where(getattr(component.c, self.ranked_in) == self.ranked_in and (component.c.rank <= new_rank ))

                        c = dbe.connect()
                        res = c.execute(req)
                        res = res.fetchall()

                        vals = list()
                        vals.append({'id' : self.id, 'rank' : new_rank})

                        if(new_rank < self.rank):
                            for row in res:
                                vals.append({'id' : row.uid, 'rank' : row.rank+1})
                        else:
                            for row in res:
                                vals.append({'id' : row.uid, 'rank' : row.rank-1})


                        req = component.update().where(component.c.uid == sql.bindparam('id')).values(rank = sql.bindparam('rank'))
                        c.execute(req, vals)
                        c.close()

                        self.rank = new_rank
                    else:
                        logger.error("Bad argument")
                        raise ValueError('new_rank to big, new_rank - 1 doesn\'t exist. new_rank = '+str((new_rank)))
                elif(sign == '+'):
                    if(new_rank != 0):
                        req = req.where(getattr(component.c, self.ranked_in) == self.ranked_in and (component.c.rank <= self.rank + new_rank and component.c.rank > self.rank))

                        c = dbe.connect()
                        res = c.execute(req)
                        res = res.fetchall()

                        vals = list()
                        vals.append({'id' : self.id, 'rank' : self.rank + new_rank})

                        for row in res:
                            vals.append({'id' : row.uid, 'rank' : row.rank - 1})

                        req = component.update().where(component.c.uid == sql.bindparam('id')).values(rank = sql.bindparam('rank'))
                        c.execute(req, vals)
                        c.close()

                        self.rank += new_rank
                    else:
                        logger.error("Bad argument")
                        raise ValueError('Excepted a positive int not a null. new_rank = '+str((new_rank)))
                elif(sign == '-'):
                    if(new_rank != 0):
                        req = req.where(getattr(component.c, self.ranked_in) == self.ranked_in and (component.c.rank >= self.rank - new_rank and component.c.rank < self.rank))

                        c = dbe.connect()
                        res = c.execute(req)
                        res = res.fetchall()

                        vals = list()
                        vals.append({'id' : self.id, 'rank' : self.rank - new_rank})

                        for row in res:
                            vals.append({'id' : row.uid, 'rank' : row.rank + 1})

                        req = component.update().where(component.c.uid == sql.bindparam('id')).values(rank = sql.bindparam('rank'))
                        c.execute(req, vals)
                        c.close()

                        self.rank -= new_rank
                    else:
                        logger.error("Bad argument")
                        raise ValueError('Excepted a positive int not a null. new_rank = '+str((new_rank)))
                else:
                    logger.error("Bad argument")
                    raise TypeError('Excepted a string (\'=\' or \'+\' or \'-\') not a '+str(type(new_rank)))
            else:
                logger.error("Bad argument")
                raise ValueError('Excepted a positive int not a negative. new_rank = '+str((new_rank)))
        else:
            logger.error("Bad argument")
            raise TypeError('Excepted a int not a '+str(type(new_rank)))


    def __repr__(self):
        if self.name is None:
            return "<%s #%s, 'non populated'>" % (type(self).__name__, self.id)
        else:
            return "<%s #%s, '%s'>" % (type(self).__name__, self.id, self.name)

    @classmethod
    def newUid(c):
        """ This function register a new component in uids table
            @return The new uid
        """
        dbe = c.getDbE()

        uidtable = sql.Table('uids', sqlutils.meta(dbe))
        conn = dbe.connect()
        req = uidtable.insert(values={'table':c.table})
        res = conn.execute(req)

        uid = res.inserted_primary_key[0]
        logger.debug("Registering a new UID '"+str(uid)+"' for '"+c.table+"' component")

        conn.close()

        return uid


class EmComponentNotExistError(Exception):
    pass
