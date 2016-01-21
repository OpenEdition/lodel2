"""
    Test for LeClass
"""

import unittest
from unittest import TestCase

import EditorialModel
import leapi
import DataSource.dummy
import leapi.test.utils

class LeClassTestCase(TestCase):
    
    @classmethod
    def setUpClass(cls):
        """ Write the generated code in a temporary directory and import it """
        cls.tmpdir = leapi.test.utils.tmp_load_factory_code()
    @classmethod
    def tearDownClass(cls):
        """ Remove the temporary directory created at class setup """
        leapi.test.utils.cleanup(cls.tmpdir)

    def test_fieldlist(self):
        """ Testing fieldlist method """
        from dyncode import Publication, Personnes, Textes, LeObject

        for leclass in [ Publication, Personnes, Textes ]:
            for fieldname in leclass.fieldlist(complete = False):
                ftype = leclass.fieldtypes()[fieldname]
                if hasattr(ftype, 'immutable'):
                    if ftype.immutable:
                        self.assertNotIn(
                            fieldname,
                            LeObject.fieldlist()
                        )
                    else:
                        self.assertIn(
                            fieldname,
                            LeObject.fieldlist()
                        )
                else:
                    self.assertNotIn(
                        fieldname,
                        LeObject.fieldlist()
                    )
            for obj_fname in LeObject.fieldlist():
                self.assertIn(
                    obj_fname,
                    leclass.fieldlist(complete = True)
                )

    def test_fieldtypes(self):
        """ Testing the fieldtypes() method """
        from dyncode import Publication, Personnes, Textes, LeObject
        for leclass in [ Publication, Personnes, Textes ]:
            for complete in [ True, False ]:
                self.assertEqual(
                    sorted(list(leclass.fieldtypes(complete).keys())),
                    sorted(leclass.fieldlist(complete)),
                )
