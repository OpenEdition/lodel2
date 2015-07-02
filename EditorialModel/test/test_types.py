import os
import logging
import datetime

from django.conf import settings
from unittest import TestCase
import unittest

from EditorialModel.types import EmType
from EditorialModel.classes import EmClass
from EditorialModel.classtypes import EmClassType, EmNature
from EditorialModel.components import EmComponent, EmComponentNotExistError
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fieldtypes import *
from EditorialModel.fields import EmField
from EditorialModel.test.utils import *
from Database import sqlutils

import sqlalchemy as sqla

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")
TEST_TYPE_DBNAME = 'test_em_type_db.sqlite'

def setUpModule():
    logging.basicConfig(level=logging.CRITICAL)

    initTestDb(TEST_TYPE_DBNAME)
    setDbConf(TEST_TYPE_DBNAME)

    emclass1 = EmClass.create("entity1", EmClassType.entity)
    emclass2 = EmClass.create("entity2", EmClassType.entity)
    emclass3 = EmClass.create("entry1", EmClassType.entry)
    emclass4 = EmClass.create("person1", EmClassType.person)

    emtype = EmType.create(name='type1', em_class=emclass2)
    EmType.create(name='type2', em_class=emclass2)
    EmType.create(name='type3', em_class=emclass2)

    EmType.create(name='type4', em_class=emclass3)
    EmType.create(name='type5', em_class=emclass3)

    EmType.create(name='type6', em_class=emclass4)
    EmType.create(name='type7', em_class=emclass4)

    emfieldgroup = EmFieldGroup.create(name='fieldgroup1', em_class=emclass1)
    emfieldgroup2 = EmFieldGroup.create(name='fieldgroup2', em_class=emclass2)
    emfieldtype = EmField_integer()
    EmField.create(name='field1', fieldgroup=emfieldgroup, fieldtype=emfieldtype, rel_to_type_id=emtype.uid)
    EmField.create(name='field2', fieldgroup=emfieldgroup2, fieldtype=emfieldtype, optional=True)
    EmField.create(name='field3', fieldgroup=emfieldgroup2, fieldtype=emfieldtype, optional=False)

    saveDbState(TEST_TYPE_DBNAME)

def tearDownModule():
    cleanDb(TEST_TYPE_DBNAME)
    pass

class TypeTestCase(TestCase):
    
    def setUp(self):
        restoreDbState(TEST_TYPE_DBNAME)
        self.emclass1 = EmClass("entity1")
        self.emclass2 = EmClass("entity2")
        self.emtype = EmType('type1')
        self.emtype2 = EmType('type2')
        self.emtype3 = EmType('type3')
        self.emtype4 = EmType('type4')
        self.emtype5 = EmType('type5')
        self.emtype6 = EmType('type6')
        self.emtype7 = EmType('type7')
        self.emfieldgroup = EmFieldGroup('fieldgroup1')
        self.emfieldtype = EmField_integer()
        self.emfield = EmField('field1')
        self.emfield2 = EmField('field2')
        self.emfield3 = EmField('field3')
        pass



class TestSelectField(TypeTestCase):
    def testSelectField(self):
        """ Testing optionnal field selection """
        self.emtype.select_field(self.emfield2)
        #a bit queick and dirty
        self.assertIn(self.emfield2, self.emtype.selected_fields()) 
        pass

    def testUnselectField(self):
        """ Testing optionnal field unselection """
        self.emtype.select_field(self.emfield2)
        self.emtype.unselect_field(self.emfield2)
        self.assertNotIn(self.emfield2, self.emtype.selected_fields())
        pass

    def testSelectFieldInvalid(self):
        """ Testing optionnal field selection with invalid fields """
        with self.assertRaises(ValueError, msg="But the field was not optionnal"):
            self.emtype.select_field(self.emfield3)
        with self.assertRaises(ValueError, msg="But the field was not part of this type"):
            self.emtype.select_field(self.emfield)
        pass

class TestLinkedTypes(TypeTestCase):
    @unittest.skip("Not yet implemented")
    def testLinkedtypes(self):
        """ Testing linked types """
        self.emtype.add_superior(self.emtype2, EmNature.PARENT)
        self.emtype3.add_superior(self.emtype, EmNature.PARENT)

        linked_types = self.emtype.linked_types()

        self.assertEqual(len(linked_types),2)
        self.assertNotIn(self.emtype,linked_types)
        self.assertIn(self.emtype2, linked_types)
        self.assertIn(self.emtype3, linked_types)

class TestTypeHierarchy(TypeTestCase):

    @staticmethod
    ## Replace instances by uid in subordinates or superiors return values
    def _hierarch_uid(subs):
        res = dict()
        for nat in subs:
            res[nat] = []
            for sub in subs[nat]:
                res[nat].append(sub.uid)
        return res

    # Check that the superior has been added
    def check_add_sup(self, subtype, suptype, relnat):
        subuid = self._hierarch_uid(suptype.subordinates())
        supuid = self._hierarch_uid(subtype.superiors())

        for nat in subuid:
            if nat == relnat:
                check = self.assertIn
                msg = " should be in "
            else:
                check = self.assertNotIn
                msg = " should not be in "
            check(subtype.uid, subuid[nat], subtype.name+msg+suptype.name+" subordinates with nature '"+nat+"'")
            check(suptype.uid, supuid[nat], suptype.name+msg+subtype.name+" superiors with nature '"+nat+"'")
        pass
            

    def testAddSuperiorParent(self):
        """ Testing add superior in relation with Parent nature """
        self.emtype.add_superior(self.emtype2, EmNature.PARENT)
        self.check_add_sup(self.emtype, self.emtype2, EmNature.PARENT)

        self.emtype4.add_superior(self.emtype4, EmNature.PARENT)
        self.check_add_sup(self.emtype4, self.emtype4, EmNature.PARENT)
        pass

    def testAddSuperiorTranslation(self):
        """ Testing add superior in relation with Translation nature """
        self.emtype.add_superior(self.emtype, EmNature.TRANSLATION)
        self.check_add_sup(self.emtype, self.emtype, EmNature.TRANSLATION)

        self.emtype4.add_superior(self.emtype4, EmNature.TRANSLATION)
        self.check_add_sup(self.emtype4, self.emtype4, EmNature.TRANSLATION)
        pass

    def testAddSuperiorIdentity(self):
        """ Testing add superior in relation with Identity nature """
        self.emtype6.add_superior(self.emtype6, EmNature.IDENTITY)
        self.check_add_sup(self.emtype6, self.emtype6, EmNature.IDENTITY)
        self.emtype6.add_superior(self.emtype7, EmNature.IDENTITY)
        self.check_add_sup(self.emtype6, self.emtype6, EmNature.IDENTITY)
        pass

    def testIllegalSuperior(self):
        """ Testing invalid add superior """
        illegal_combinations = [
            (self.emtype, self.emtype4, EmNature.PARENT),
            (self.emtype, self.emtype2, EmNature.TRANSLATION),
            (self.emtype4, self.emtype5, EmNature.PARENT),
            (self.emtype4, self.emtype5, EmNature.TRANSLATION),
            (self.emtype6, self.emtype, EmNature.IDENTITY),
            (self.emtype4, self.emtype, EmNature.PARENT),
            (self.emtype6, self.emtype, EmNature.PARENT),
            (self.emtype, self.emtype2, EmNature.IDENTITY),

        ]
        for t1, t2, rnat in illegal_combinations:
            with self.assertRaises(ValueError, msg="When trying to add an illegal superior "+str(t2)+" to "+str(t1)+" with '"+rnat+"' as relation nature"):
                t1.add_superior(t2, rnat)
        pass
    
    def testDelSuperior(self):
        """ Testing superior deletion """
        self.emtype.add_superior(self.emtype2, EmNature.PARENT)
        self.emtype.add_superior(self.emtype, EmNature.PARENT)
        self.emtype.add_superior(self.emtype, EmNature.TRANSLATION)

        self.emtype.del_superior(self.emtype2, EmNature.PARENT)
        supuid = self._hierarch_uid(self.emtype.superiors())
        self.assertNotIn(self.emtype2.uid, supuid[EmNature.PARENT], str(self.emtype2)+" should have been deleted as superior of "+str(self.emtype))

        self.assertIn(self.emtype.uid, supuid[EmNature.PARENT], "Deleted more than wanted in the same relation nature")
        self.assertIn(self.emtype.uid, supuid[EmNature.TRANSLATION], "Deleted more than wanted in another relation nature")
        pass
        
        

class TestDeleteTypes(TypeTestCase):
    def testDeleteTypes(self):
        """ Testing EmType deletion """
        type_name = self.emtype.name
        self.assertTrue(self.emtype.delete(), "delete method returns False but should return True")
        with self.assertRaises(EmComponentNotExistError, msg="Type not deleted"):
            EmType(type_name)

    def testUndeletableTypes(self):
        """ Testing invalid non empty EmType deletion """
        type_name = self.emtype.name
        self.emtype2.add_superior(self.emtype, 'parent')
        self.assertFalse(self.emtype.delete(), "delete return True but should return False")
        try:
            tmptype = EmType(type_name)
        except EmComponentNotExistError:
            self.fail("The type was deleted but it has subordinates when deleted")
        pass

