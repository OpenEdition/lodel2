#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent
from EditorialModel.classes import EmClass
import EditorialModel.fieldtypes as ftypes

# from Database import sqlutils
# import sqlalchemy as sql

# import EditorialModel


## Represents groups of EmField associated with an EmClass
#
# EmClass fields representation is organised with EmFieldGroup
# @see EditorialModel::fields::EmField EditorialModel::classes::EmClass
class EmFieldGroup(EmComponent):

    ## The database table name
    table = 'em_fieldgroup'
    ranked_in = 'class_id'

    ## List of fields
    _fields = [('class_id', ftypes.EmField_integer)]

    @classmethod
    ## Create a new EmFieldGroup
    #
    # Save it in database and return an instance*
    # @param name str: The name of the new EmFieldGroup
    # @param em_class EmClass : An EditorialModel::classes::EmClass instance
    # @param **em_component_args : @ref EditorialModel::components::create()
    # @throw EmComponentExistError If an EmFieldGroup with this name allready exists
    # @throw TypeError If an argument is of an unexepted type
    def create(cls, name, em_class, **em_component_args):
        if not isinstance(name, str):
            raise TypeError("Excepting <class str> as name. But got %s" % str(type(name)))
        if not isinstance(em_class, EmClass):
            raise TypeError("Excepting <class EmClass> as em_class. But got %s" % str(type(name)))

        return super(EmFieldGroup, cls).create(name=name, class_id=em_class.uid, **em_component_args)

    ## Get the list of associated fields
    # @return A list of EmField instance
    def fields(self):
        result = []
        for _,field in self.components['field']:
            if field.fieldgroup_id==self.uid:
                result.append(field)
        return result
        # meta = sqlutils.meta(self.db_engine)
        # field_table = sql.Table(EditorialModel.fields.EmField.table, meta)
        # req = field_table.select(field_table.c.uid).where(field_table.c.fieldgroup_id == self.uid)
        # conn = self.db_engine.connect()
        # res = conn.execute(req)
        # rows = res.fetchall()
        # conn.close()
        # return [EditorialModel.fields.EmField(row['uid']) for row in rows]
