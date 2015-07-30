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

#from EditorialModel.test.utils import *
from Lodel.utils.mlstring import MlString
from Database import sqlutils

import sqlalchemy as sqla

from EditorialModel.model import Model
from EditorialModel.backend.json_backend import EmBackendJson
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

#=###########=#
# TESTS SETUP #
#=###########=#

TEST_FIELDGROUP_DBNAME = 'test_em_fieldgroup_db.sqlite'

EM_TEST = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'me.json')
EM_TEST_OBJECT = None


def setUpModule():
    global EM_TEST_OBJECT
    EM_TEST_OBJECT = Model(EmBackendJson(EM_TEST))

    logging.basicConfig(level=logging.CRITICAL)

    #initTestDb(TEST_FIELDGROUP_DBNAME)
    #setDbConf(TEST_FIELDGROUP_DBNAME)
    
    #Classes creation
    #EmClass.create("entity1", EmClassType.entity)
    #EmClass.create("entity2", EmClassType.entity)
    #EmClass.create("entry1", EmClassType.entry)
    #EmClass.create("entry2", EmClassType.entry)
    #EmClass.create("person1", EmClassType.person)
    #EmClass.create("person2", EmClassType.person)

    #saveDbState(TEST_FIELDGROUP_DBNAME)

    #shutil.copyfile(TEST_FIELDGROUP_DBNAME, globals()['fieldgroup_test_dbfilename']+'_bck')


def tearDownModule():
    #cleanDb(TEST_FIELDGROUP_DBNAME)
    pass


class FieldGroupTestCase(TestCase):
    
    def setUp(self):
        #restoreDbState(TEST_FIELDGROUP_DBNAME)
        pass


#======================#
# EmFielgroup.__init__ #
#======================#
class TestInit(FieldGroupTestCase):
    '''
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
    '''

    def setUp(self):
        super(TestInit, self).setUp()
        self.tfgs = [
            {"name": "testfg1", "string": MlString({"fre": "Gens"}), "help_text": MlString({}), "class_id": 1},
            {"name": "testfg2", "string": MlString({"fre": "Gens"}), "help_text": MlString({}), "class_id": 1},
            {"name": "testfg3", "string": MlString({"fre": "Civilité"}), "help_text": MlString({}), "class_id": 2}
        ]
        for tfg in self.tfgs:
            fieldgroup = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, tfg)

    def test_init(self):
        """ Test that EmFieldgroup are correctly instanciated compare to self.tfg """
        for tfg in self.tfgs:
            fieldgroup = EM_TEST_OBJECT.component(tfg['uid'])
            for attr in tfg:
                if attr != 'uid':
                    v = tfg[attr]
                    self.assertEqual(getattr(fieldgroup, attr), v, "The '"+attr+"' property fetched from backend doesn't match the excepted value")


    def test_init_badargs(self):
        """ Tests that EmFieldGroup init fails when bad arguments are given"""
        baduid = self.tfgs[2]['uid'] + 4096
        badname = 'NonExistingName'

        # TODO Voir si on garde le return False de Model.component() ou si on utilise plutôt une exception EmComponentNotExistError en modifiant le reste du code source pour gérer ce cas
        self.assertFalse(EM_TEST_OBJECT.component(baduid), msg="Should be False because fieldgroup with id " + str(baduid) + " should not exist")
        self.assertFalse(EM_TEST_OBJECT.component(badname), msg="Should be False because fieldgroup with id " + str(badname) + " should not exist")
        self.assertFalse(EM_TEST_OBJECT.component(print), msg="Should be False when crazy arguments are given")
        self.assertFalse(EM_TEST_OBJECT.component(['hello', 'world']), msg="Should be False when crazy arguments are given")


'''
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

'''
