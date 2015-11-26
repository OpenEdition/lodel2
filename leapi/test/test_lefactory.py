import unittest
from unittest import TestCase

import tempfile
import sys
import shutil

import EditorialModel
import leapi
import leapi.test.utils
from leapi.lefactory import LeFactory

class TestLeFactorySyntax(TestCase):

    def test_generated_code_syntax(self):
        fact = LeFactory('leapi/dyn.py')
        py = fact.generate_python(**leapi.test.utils.genepy_args)
        pyc = compile(py, "dyn.py", 'exec')
        exec(pyc, globals())

class TestLeFactory(TestCase):
    
    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leapi.test.utils.cleanup(cls.tmpdir)

    def setUp(self):
        self.model = leapi.test.utils.genepy_args['model']

    def test_leobject(self):
        """ Testing the generated LeObject class """
        import dyncode
        from dyncode import LeType, LeClass

        self.assertTrue(hasattr(dyncode, 'LeObject'))

        for uid, cls in dyncode.LeObject._me_uid.items():
            if LeType in cls.__bases__:
                self.assertNotEqual(cls, LeType)
                self.assertEqual(cls._type_id, uid)
            elif LeClass in cls.__bases__:
                self.assertNotEqual(cls, LeClass)
                self.assertEqual(cls._class_id, uid)
            else:
                self.fail("Bad instance type for _me_uid values : %s"%type(cls))

    ## @todo Testing _fieldtypes attribute but we need an __hash__ method on fieldtypes
    def test_leclass(self):
        """ Testing generated LeClass childs classes """
        import dyncode
        from dyncode import LeType, LeClass

        for emclass in self.model.components(EditorialModel.classes.EmClass):
            leclass_name = LeFactory.name2classname(emclass.name)
            self.assertTrue(hasattr(dyncode, leclass_name))

            leclass = getattr(dyncode, leclass_name)
            self.assertEqual(leclass._class_id, emclass.uid)
            
            #Testing inheritance
            self.assertEqual(set(leclass.__bases__), set([dyncode.LeObject, dyncode.LeClass]))
            
            #Testing _linked_types attr
            self.assertEqual(
                set([ LeFactory.name2classname(lt.name) for lt in emclass.linked_types()]),
                set([ t.__name__ for t in leclass._linked_types ])
            )

            #Testing fieldtypes
            self.assertEqual(
                set([ f.name for f in emclass.fields(relational=False)]),
                set(leclass._fieldtypes.keys())
            )
            for field in emclass.fields(relational=False):
                self.assertEqual(
                    hash(field.fieldtype_instance()),
                    hash(leclass._fieldtypes[field.name])
                )


    def test_letype(self):
        """ Testing generated LeType childs classes """
        import dyncode
        from dyncode import LeType, LeClass

        for emtype in self.model.components(EditorialModel.types.EmType):
            letype_name = LeFactory.name2classname(emtype.name)
            self.assertTrue(hasattr(dyncode, letype_name))

            letype = getattr(dyncode, letype_name)
            self.assertEqual(letype._type_id, emtype.uid)
            self.assertEqual(letype._leclass._class_id, emtype.em_class.uid)

            #Testing inheritance
            self.assertEqual(
                set(letype.__bases__),
                set([LeType, letype._leclass])
            )

            #Testing _fields
            self.assertEqual(
                set([ f.name for f in emtype.fields(False) ]),
                set([ f for f in letype._fields])
            )

            #Testing superiors
            for nat, sups in emtype.superiors().items():
                self.assertIn(nat, letype._superiors.keys())
                self.assertEqual(
                    set([ s.__name__ for s in letype._superiors[nat]]),
                    set([ LeFactory.name2classname(s.name) for s in sups])
                )

