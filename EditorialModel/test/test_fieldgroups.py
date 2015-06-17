import os
import logging

from django.conf import settings

from unittest import TestCase
import unittest

from EditorialModel.components import EmComponent
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.classes import EmClass
from EditorialModel.classtypes import EmClassType

from Database.sqlsetup import SQLSetup
import Database.sqlutils

import sqlalchemy as sqla

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

#=###########=#
# TESTS SETUP #
#=###########=#

def setUpModule():
    #Overwritting db confs to make tests
    settings.LODEL2SQLWRAPPER = {
        'default': {
            'ENGINE': 'sqlite',
            'NAME': '/tmp/testdb.sqlite'
        }
    }

    logging.basicConfig(level=logging.CRITICAL)

class FieldGroupTestCase(TestCase):
    
    def setUp(self):
        sqls = SQLSetup()
        sqls.initDb()
        #Samples values insertion

        #Classes creation
        EmClass.create("entity1", EmClassType.entity)
        EmClass.create("entity2", EmClassType.entity)
        EmClass.create("entry1", EmClassType.entry)
        EmClass.create("entry2", EmClassType.entry)
        EmClass.create("person1", EmClassType.person)
        EmClass.create("person2", EmClassType.person)
        pass


#======================#
# EmFielgroup.__init__ #
#======================#
class TestInit(FieldGroupTestCase):

    def setUp(self):
        super(TestInit, self).setUp()
        conn = getEngine().connect()
        
        ent1 = EmClass('entity1')
        idx1 = EmClass('index1')

        self.tfg = [
            { 'uid': EmFieldGroup.newUid(), 'name': 'fg1', 'string': '{"fr":"Super Fieldgroup"}', 'help': '{"en":"help"}', 'rank': 0 , 'class_id': ent1.uid},
            { 'uid': EmFieldGroup.newUid(), 'name': 'fg2', 'string': '{"fr":"Super Fieldgroup"}', 'help': '{"en":"help"}', 'rank': 1 , 'class_id': ent1.uid},
            { 'uid': EmFieldGroup.newUid(), 'name': 'fg3', 'string': '{"fr":"Super Fieldgroup"}', 'help': '{"en":"help"}', 'rank': 2 , 'class_id': idx1.uid},
        ]

        req = sqla.Table('em_fieldgroup').insert(self.tfg)
        conn.execute(req)
        pass

    def testinit(self):
        fg1 = EmFieldGroup('fg1')

        for tfg in self.tfg:
            fg = EmFieldGroup(tfg['name'])
            for attr in tfg:
                self.assertEqual(getattr(fg, attr), tfg[attr], "The properties fetched from Db don't match excepted value")


