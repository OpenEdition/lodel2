import os
import logging

from unittest import TestCase

from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.classes import EmClass
from EditorialModel.types import EmType
from EditorialModel.fields import EmField
from Lodel.utils.mlstring import MlString
from EditorialModel.model import Model
from EditorialModel.backend.json_backend import EmBackendJson

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


def tearDownModule():
    pass


class FieldGroupTestCase(TestCase):

    def setUp(self):
        pass


#======================#
# EmFielgroup.__init__ #
#======================#
class TestInit(FieldGroupTestCase):

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
                    self.assertEqual(getattr(fieldgroup, attr), v, "The '" + attr + "' property fetched from backend doesn't match the excepted value")

    def test_init_badargs(self):
        """ Tests that EmFieldGroup init fails when bad arguments are given"""
        baduid = self.tfgs[2]['uid'] + 4096
        badname = 'NonExistingName'

        # TODO Voir si on garde le return False de Model.component() ou si on utilise plutôt une exception EmComponentNotExistError en modifiant le reste du code source pour gérer ce cas
        self.assertFalse(EM_TEST_OBJECT.component(baduid), msg="Should be False because fieldgroup with id " + str(baduid) + " should not exist")
        self.assertFalse(EM_TEST_OBJECT.component(badname), msg="Should be False because fieldgroup with id " + str(badname) + " should not exist")
        self.assertFalse(EM_TEST_OBJECT.component(print), msg="Should be False when a function name is given as argument")
        with self.assertRaises(TypeError, msg="Should raise when crazy arguments are given"):
            fieldgroup = EM_TEST_OBJECT.component(['hello', 'world'])


#=====================#
# EmFieldgroup.create #
#=====================#
class TestCreate(FieldGroupTestCase):

    def test_create(self):
        """Does create actually create a fieldgroup ?"""
        params = {
            'EmClass entity instance': EM_TEST_OBJECT.component(1),
            'EmClass entry instance': EM_TEST_OBJECT.component(2)
        }

        for i, param_name in enumerate(params):
            arg = params[param_name]
            if isinstance(arg, EmClass):
                cl = arg
            else:
                cl = EM_TEST_OBJECT.component(arg)

            fieldgroup_name = 'new_fg' + str(i)
            fieldgroup = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': fieldgroup_name, 'class_id': arg.uid})
            self.assertEqual(fieldgroup.name, fieldgroup_name, "Model.create_component() doesn't instanciate name correctly")
            self.assertEqual(fieldgroup.class_id, cl.uid, "Model.create_component() doesn't instanciate class_id correctly")

            nfg = EM_TEST_OBJECT.component(fieldgroup.uid)

            # Checking object property
            for fname in fieldgroup.__dict__:
                self.assertEqual(getattr(nfg, fname), getattr(fieldgroup, fname), "Msg inconsistency when a created fieldgroup is fetched from the backend (in " + fname + " property)")

    def test_create_badargs(self):
        """ Does create fails when badargs given ? """
        badargs = {
            'EmClass type (not an instance)': EmClass,
            'Non Existing id': 9000,
            'Another component instance': EM_TEST_OBJECT.create_component(EmType.__name__, {'name': 'fooType', 'class_id': EM_TEST_OBJECT.component(1).uid}),
            'A function': print
        }

        for i, badarg_name in enumerate(badargs):
            with self.assertRaises(TypeError, msg="Should raise because trying to give " + badarg_name + " an em_class object as value"):
                fieldgroup = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': 'new_fg' + i, 'class_id': badargs[badarg_name].uid})

        # Creating a fieldgroup to test duplicate name
        exfg = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': 'existingfg', 'class_id': EM_TEST_OBJECT.component(1).uid})
        badargs = {
            'an integer': (42, AttributeError),
            'a function': (print, AttributeError),
            'an EmClass': (EM_TEST_OBJECT.component(2), AttributeError)
        }
        for badarg_name in badargs:
            (badarg, expt) = badargs[badarg_name]
            with self.assertRaises(expt, msg="Should raise because trying to give " + badarg_name + " as first argument"):
                fieldgroup = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': badarg, 'class_id': EM_TEST_OBJECT.component(1).uid})


#=====================#
# EmFieldgroup.fields #
#=====================#
class TestFields(FieldGroupTestCase):

    def setUp(self):
        super(TestFields, self).setUp()
        self.fg1 = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': 'testfg1', 'class_id': EM_TEST_OBJECT.component(1).uid})
        self.fg2 = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': 'testfg2', 'class_id': EM_TEST_OBJECT.component(2).uid})
        self.fg3 = EM_TEST_OBJECT.create_component(EmFieldGroup.__name__, {'name': 'testfg3', 'class_id': EM_TEST_OBJECT.component(1).uid})

    def test_fields(self):
        """ Does it returns actually associated fields ? """
        # Creating fields
        test_fields1 = [
            {'name': 'field1', 'fieldgroup_id': self.fg1.uid, 'fieldtype': 'integer'},
            {'name': 'field2', 'fieldgroup_id': self.fg1.uid, 'fieldtype': 'integer'},
            {'name': 'field4', 'fieldgroup_id': self.fg1.uid, 'fieldtype': 'integer'}
        ]

        test_fields2 = [
            {'name': 'field3', 'fieldgroup_id': self.fg2.uid, 'fieldtype': 'integer'}
        ]

        expected1 = []

        for finfo in test_fields1:
            field = EM_TEST_OBJECT.create_component(EmField.__name__, finfo)
            expected1.append(field.uid)

        for finfo in test_fields2:
            field = EM_TEST_OBJECT.create_component(EmField.__name__, finfo)

        expected1 = set(expected1)

        tests = {
            'newly': EM_TEST_OBJECT.component(self.fg1.uid),
            'old': self.fg1
        }

        for name in tests:
            fieldgroup = tests[name]
            flist = fieldgroup.fields()
            res = []
            for field in flist:
                res.append(field.uid)
            self.assertEqual(set(res), set(expected1))

    def test_non_relational(self):
        """ Check that relationnal=False returns only non relational fields """
        for fgrp in [ self.fg1, self.fg2, self.fg3 ]:
            for field in fgrp.fields(relational=False):
                self.assertTrue(field.fieldtype != 'rel2type' and field.rel_field_id is None)

    def test_empty_fields(self):
        """ Testing fields method on an empty fieldgroup """
        fieldgroup = self.fg3
        fields_list = fieldgroup.fields()
        self.assertEqual(len(fields_list), 0)
