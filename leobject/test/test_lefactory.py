import unittest
from unittest import TestCase

import tempfile
import sys
import shutil

import EditorialModel
import leobject
import leobject.test.utils
from leobject.lefactory import LeFactory

class TestLeFactorySyntax(TestCase):

    def test_generated_code_syntax(self):
        py = LeFactory.generate_python(**leobject.test.utils.genepy_args)
        pyc = compile(py, "dyn.py", 'exec')
        exec(pyc, globals())

class TestLeFactory(TestCase):
    
    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leobject.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leobject.test.utils.cleanup(cls.tmpdir)

    def setUp(self):
        backend=leobject.test.utils.genepy_args['backend_cls'](**leobject.test.utils.genepy_args['backend_args'])
        self.model = EditorialModel.model.Model(backend = backend)

    def test_leobject(self):
        """ Testing the generated LeObject class """
        import dyncode
        self.assertTrue(hasattr(dyncode, 'LeObject'))

        for uid, cls in dyncode.LeObject._me_uid.items():
            if leobject.letype.LeType in cls.__bases__:
                self.assertNotEqual(cls, leobject.letype.LeType)
                self.assertEqual(cls._type_id, uid)
            elif leobject.leclass.LeClass in cls.__bases__:
                self.assertNotEqual(cls, leobject.leclass.LeClass)
                self.assertEqual(cls._class_id, uid)
            else:
                self.fail("Bad instance type for _me_uid values : %s"%type(cls))

    ## @todo Testing _fieldtypes attribute but we need an __hash__ method on fieldtypes
    def test_leclass(self):
        """ Testing generated LeClass childs classes """
        import dyncode

        for emclass in self.model.components(EditorialModel.classes.EmClass):
            leclass_name = LeFactory.name2classname(emclass.name)
            self.assertTrue(hasattr(dyncode, leclass_name))

            leclass = getattr(dyncode, leclass_name)
            self.assertEqual(leclass._class_id, emclass.uid)
            
            #Testing inheritance
            self.assertEqual(set(leclass.__bases__), set([dyncode.LeObject, leobject.leclass.LeClass]))
            
            #Testing _fieldgroups attr
            self.assertEqual(
                set([ fg.name for fg in emclass.fieldgroups()]),
                set(leclass._fieldgroups.keys())
            )
            for fgroup in emclass.fieldgroups():
                self.assertEqual(
                    set([ f.name for f in fgroup.fields()]),
                    set(leclass._fieldgroups[fgroup.name])
                )
            
            #Testing _linked_types attr
            self.assertEqual(
                set([ LeFactory.name2classname(lt.name) for lt in emclass.linked_types()]),
                set([ t.__name__ for t in leclass._linked_types ])
            )

            #Testing fieldtypes
            self.assertEqual(
                set([ f.name for f in emclass.fields()]),
                set(leclass._fieldtypes.keys())
            )
            for field in emclass.fields():
                self.assertEqual(
                    hash(field.fieldtype_instance()),
                    hash(leclass._fieldtypes[field.name])
                )


    def test_letype(self):
        """ Testing generated LeType childs classes """
        import dyncode

        for emtype in self.model.components(EditorialModel.types.EmType):
            letype_name = LeFactory.name2classname(emtype.name)
            self.assertTrue(hasattr(dyncode, letype_name))

            letype = getattr(dyncode, letype_name)
            self.assertEqual(letype._type_id, emtype.uid)
            self.assertEqual(letype._leclass._class_id, emtype.em_class.uid)

            #Testing inheritance
            self.assertEqual(
                set(letype.__bases__),
                set([leobject.letype.LeType, letype._leclass])
            )

            #Testing _fields
            self.assertEqual(
                set([ f.name for f in emtype.fields() ]),
                set(letype._fields)
            )

            #Testing superiors
            for nat, sups in emtype.superiors().items():
                self.assertIn(nat, letype._superiors.keys())
                self.assertEqual(
                    set([ s.__name__ for s in letype._superiors[nat]]),
                    set([ LeFactory.name2classname(s.name) for s in sups])
                )

