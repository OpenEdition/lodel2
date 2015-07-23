#-*- coding: utf-8 -*-

from EditorialModel.components import EmComponent
from EditorialModel.classes import EmClass
import EditorialModel.fieldtypes as ftypes
from EditorialModel.fields import EmField

#from Database import sqlutils
#import sqlalchemy as sql

#import EditorialModel


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

    def __init__(self, data, model):
        super(EmFieldGroup, self).__init__(data, model)

    @classmethod
    ## Create a new EmFieldGroup
    #
    # Save it in database and return an instance*
    # @param **em_component_args : @ref EditorialModel::components::create(), must contain fields "name" (str) and "class" (EmClass)
    # @throw EmComponentExistError If an EmFieldGroup with this name allready exists
    # @throw TypeError If an argument is of an unexepted type
    def create(cls, **em_component_args):
        fieldgroup_name = em_component_args['name']
        fieldgroup_class = em_component_args['class']

        if not isinstance(fieldgroup_name, str):
            raise TypeError("Excepting <class str> as name. But got %s" % str(type(fieldgroup_name)))
        if not isinstance(fieldgroup_class, EmClass):
            raise TypeError("Excepting <class EmClass> as em_class. But got %s" % str(type(fieldgroup_class)))

        return super(EmFieldGroup, cls).create(**em_component_args)

    ## Deletes a fieldgroup
    #
    # @return True if the deletion is a success, False if not
    def delete(self):
        # all the EmField objects contained in this fieldgroup should be deleted first
        fieldgroup_fields = self.fields()
        if len(fieldgroup_fields)>0:
            raise NotEmptyError("This Fieldgroup still contains fields. It can't be deleted then")
        # then we delete this fieldgroup
        return self.model.delete_component(self.uid)

    ## Get the list of associated fields
    # @return A list of EmField instance
    def fields(self):
        result = []
        for _, field in self.model.components(EmField):
            if field.fieldgroup_id == self.uid:
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

class NotEmptyError(Exception):
    pass
