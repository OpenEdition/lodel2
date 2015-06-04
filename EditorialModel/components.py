# -*- coding: utf-8 -*-

""" Main object to manipulate Editorial Model
    parent of all other EM editing classes
    @see EmClass, EmType, EmFieldGroup, EmField
"""

from Lodel.utils.mlstring import MlString
from Database.sqlwrapper import SqlWrapper
from Database.sqlobject import SqlObject
import logging
import sqlalchemy as sql

logger = logging.getLogger('Lodel2.EditorialModel')

class EmComponent(object):

    """ instaciate an EmComponent
        @param id_or_name int|str: name or id of the object
        @exception TypeError
    """
    def __init__(self, id_or_name):
        SqlWrapper.start()
        if self is EmComponent:
            raise EnvironmentError('Abstract class')
        if isinstance(id_or_name, int):
            self.id = id_or_name
        elif isinstance(id_or_name, str):
            self.id = None
            self.name = id_or_name
            self.populate()
        else:
            raise TypeError('Bad argument: expecting <int> or <str>')

    """ Lookup in the database properties of the object to populate the properties
    """
    def populate(self):
        table = SqlObject(self.table)
        select = table.sel

        if self.id is None:
            select.where(table.col.name == self.name)
        else:
            select.where(table.col.id == self.id)

        sqlresult = table.rexec(select)
        records = sqlresult.fetchall()

        if not records:
            # could have two possible Error message for id and for name
            raise EmComponentNotExistError("Bad id_or_name: could not find the component")

        for record in records:
            row = type('row', (object,), {})()
            for k in record.keys():
                setattr(row, k, record[k])

        self.id = row.uid
        self.name = row.name
        self.rank = 0 if row.rank is None else int(row.rank)
        self.date_update = row.date_update
        self.date_create = row.date_create
        self.string = MlString.load(row.string)
        self.help = MlString.load(row.help)

        return row

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

        emclass = SqlObject(self.table)
        update = emclass.table.update(values=values)
        res = emclass.wexec(update)

    """ delete this component data in the database
        @return bool
    """
    def delete(self):
        pass

    """ change the rank of the component
        @param int new_rank new position
    """
    def modify_rank(self, new_rank):
        pass

class EmComponentNotExistError(Exception):
    pass
