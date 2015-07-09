import os
import logging
import datetime
import shutil

from django.conf import settings

from unittest import TestCase
import unittest

from EditorialModel.components import EmComponent, EmComponentNotExistError
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.classes import EmClass
from EditorialModel.types import EmType
from EditorialModel.fields import EmField
from EditorialModel.classtypes import EmClassType
from EditorialModel.fieldtypes import *

from EditorialModel.test.utils import *

from Database import sqlutils

import sqlalchemy as sqla

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

#=###########=#
# TESTS SETUP #
#=###########=#

TEST_FIELDGROUP_DBNAME = 'test_em_fieldgroup_db.sqlite'

def setUpModule():

    logging.basicConfig(level=logging.CRITICAL)

    initTestDb(TEST_FIELDGROUP_DBNAME)
    setDbConf(TEST_FIELDGROUP_DBNAME)
    
    #Classes creation
    EmClass.create("entity1", EmClassType.entity)
    EmClass.create("entity2", EmClassType.entity)
    EmClass.create("entry1", EmClassType.entry)
    EmClass.create("entry2", EmClassType.entry)
    EmClass.create("person1", EmClassType.person)
    EmClass.create("person2", EmClassType.person)

    saveDbState(TEST_FIELDGROUP_DBNAME)

    #shutil.copyfile(TEST_FIELDGROUP_DBNAME, globals()['fieldgroup_test_dbfilename']+'_bck')

def tearDownModule():
    cleanDb(TEST_FIELDGROUP_DBNAME)
    pass

class FieldGroupTestCase(TestCase):
    
    def setUp(self):
        restoreDbState(TEST_FIELDGROUP_DBNAME)
        pass


#======================#
# EmFielgroup.__init__ #
#======================#
class TestInit(FieldGroupTestCase):

    def setUp(self):
        super(TestInit, self).setUp()
        dbe = sqlutils.get_engine()
        conn = sqlutils.get_engine().connect()

        ent1 = EmClass('entity1')
        idx1 = EmClass('entry1')


        self.creadate = datetime.datetime.utcnow()
        #Test fieldgroup
        self.tfg = [
            { 'uid': EmFieldGroup.new_uid(dbe), 'name': 'fg1', 'string': '{"fr":"Super Fieldgroup"}', 'help': '{"en":"help"}', 'rank': 0 , 'class_id': ent1.uid, 'date_create' : self.creadate, 'date_update': self.creadate},
            { 'uid': EmFieldGroup.new_uid(dbe), 'name': 'fg2', 'string': '{"fr":"Super Fieldgroup"}', 'help': '{"en":"help"}', 'rank': 1 , 'class_id': ent1.uid, 'date_create': self.creadate, 'date_update': self.creadate},
            { 'uid': EmFieldGroup.new_uid(dbe), 'name': 'fg3', 'string': '{"fr":"Super Fieldgroup"}', 'help': '{"en":"help"}', 'rank': 2 , 'class_id': idx1.uid, 'date_create': self.creadate, 'date_update': self.creadate},
        ]

        req = sqla.Table('em_fieldgroup', sqlutils.meta(sqlutils.get_engine())).insert(self.tfg)
        conn.execute(req)
        conn.close()
        pass

    def test_init(self):
        """ Test that EmFieldgroup are correctly instanciated compare to self.tfg """
        for tfg in self.tfg:
            fg = EmFieldGroup(tfg['name'])
            for attr in tfg:
                if attr in ['string', 'help']:
                    v = MlString.load(tfg[attr])
                else:
                    v = tfg[attr]
                self.assertEqual(getattr(fg, attr), v, "The propertie '"+attr+"' fetched from Db don't match excepted value")

        for tfg in self.tfg:
            fg = EmFieldGroup(tfg['uid'])
            for attr in tfg:
                if attr in ['string', 'help']:
                    v = MlString.load(tfg[attr])
                else:
                    v = tfg[attr]
                self.assertEqual(getattr(fg, attr), v, "The propertie '"+attr+"' fetched from Db don't match excepted value")

        pass

    def test_init_badargs(self):
        """ Test that EmFieldgroup fail when bad arguments are given """
        baduid = self.tfg[2]['uid'] + 4096
        badname = 'NonExistingName'

        with self.assertRaises(EmComponentNotExistError, msg="Should raise because fieldgroup with id "+str(baduid)+" should not exist"):
            fg = EmFieldGroup(baduid)
        with self.assertRaises(EmComponentNotExistError, msg="Should raise because fieldgroup named "+badname+" should not exist"):
            fg = EmFieldGroup(badname)
        with self.assertRaises(TypeError, msg="Should raise a TypeError when crazy arguments are given"):
            fg = EmFieldGroup(print)
        with self.assertRaises(TypeError, msg="Should raise a TypeError when crazy arguments are given"):
            fg = EmFieldGroup(['hello', 'world'])
        pass

#=====================#
# EmFieldgroup.create #
#=====================#
class TestCreate(FieldGroupTestCase):

    def test_create(self):
        """ Does create actually create a fieldgroup ? """

        params = {  'EmClass entity instance': EmClass('entity1'),
                    'EmClass entry instance': EmClass('entry1'),
                    'EmClass person instance': EmClass('person1'),
                }

        for i,param_name in enumerate(params):
            arg = params[param_name]
            if isinstance(arg, EmClass):
                cl = arg
            else:
                cl = EmClass(arg)

            fgname = 'new_fg'+str(i)
            fg = EmFieldGroup.create(fgname, arg)
            self.assertEqual(fg.name, fgname, "EmFieldGroup.create() dont instanciate name correctly")
            self.assertEqual(fg.class_id, cl.uid, "EmFieldGroup.create() dont instanciate class_id correctly")

            nfg = EmFieldGroup(fgname)

            #Checking object property
            for fname in fg._fields:
                self.assertEqual(getattr(nfg,fname), getattr(fg,fname), "Msg inconsistency when a created fieldgroup is fecthed from Db (in "+fname+" property)")
        pass

    def test_create_badargs(self):
        """ Does create fails when badargs given ? """

        badargs = { 'EmClass type (not an instance)': EmClass,
                    'Non Existing name': 'fooClassThatDontExist',
                    'Non Existing Id': 4042, #Hope that it didnt exist ;)
                    'Another component instance': EmType.create('fooType', EmClass('entity1')),
                    'A function': print
                }
        for i,badarg_name in enumerate(badargs):
            with self.assertRaises(TypeError, msg="Should raise because trying to give "+badarg_name+" as em_class"):
                fg = EmFieldGroup.create('new_fg'+i, badargs[badarg_name])

        #Creating a fieldgroup to test duplicate name
        exfg = EmFieldGroup.create('existingfg', EmClass('entity1'))

        badargs = { 'an integer': (42, TypeError),
                    'a function': (print, TypeError),
                    'an EmClass': (EmClass('entry1'), TypeError),
                }
        for badarg_name in badargs:
            (badarg,expt) = badargs[badarg_name]
            with self.assertRaises(expt, msg="Should raise because trying to give "+badarg_name+" as first argument"):
                fg = EmFieldGroup.create(badarg, EmClass('entity1'))

#=====================#
# EmFieldgroup.fields #
#=====================#
class TestFields(FieldGroupTestCase):

    def setUp(self):
        super(TestFields, self).setUp()
        self.fg1 = EmFieldGroup.create('testfg', EmClass('entity1'))
        self.fg2 = EmFieldGroup.create('testfg2', EmClass('entry1'))
        self.fg3 = EmFieldGroup.create('testfg3', EmClass('entry1'))


    def test_fields(self):
        """ Does it returns actually associated fields ? """

        #Creating fields
        test_fields1 = [
            { 'name': 'field1', 'fieldgroup': self.fg1, 'fieldtype': EmField_integer() },
            { 'name': 'field2', 'fieldgroup': self.fg1, 'fieldtype': EmField_integer() },
            { 'name': 'field4', 'fieldgroup': self.fg1, 'fieldtype': EmField_integer() },
        ]

        test_fields2 = [ 
            { 'name': 'field3', 'fieldgroup': self.fg2, 'fieldtype': EmField_integer() },
        ]

        excepted1 = []

        for finfo in test_fields1:
            f = EmField.create(**finfo)
            excepted1.append(f.uid)

        for finfo in test_fields2:
            f = EmField.create(**finfo)

        excepted1 = set(excepted1)

        tests = {
            'newly': EmFieldGroup('testfg'),
            'old' : self.fg1
        }

        for name in tests:
            fg = tests[name]
            flist = fg.fields()
            res = []
            for f in flist:
                res.append(f.uid)
            self.assertEqual(set(res), set(excepted1))

    def test_empty_fields(self):
        """ Testing fields method on an empty fieldgroup """
        fg = self.fg3
        flist = fg.fields()
        self.assertEqual(len(flist), 0)
        pass

