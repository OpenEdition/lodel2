import unittest

from EditorialModel.model import Model
from EditorialModel.classtypes import EmNature
from EditorialModel.backend.json_backend import EmBackendJson

class TypeTestCase(unittest.TestCase):

    def setUp(self):
        self.me = Model(EmBackendJson('EditorialModel/test/me.json'))
        self.rubrique = self.me.component(14)
        self.article = self.me.component(5)
        self.personne = self.me.component(6)
        self.soustitre_field = self.me.component(7)
        self.age_field = self.me.component(18)
        self.nom_field = self.me.component(9)
        self.numero = self.me.component(19)
        self.gens_group = self.me.component(17)
        self.info_group = self.me.component(3)
        self.couleur_group = self.me.component(20)
        self.couleur_field = self.me.component(21)

class TestSelectField(TypeTestCase):

    def testSelectField(self):
        """ Testing optionnal field selection """
        self.personne.select_field(self.age_field)

        self.assertIn(self.age_field, self.personne.selected_fields())
        self.assertIn(self.age_field.uid, self.personne.fields_list)

    def testUnselectField(self):
        """ Testing optionnal field unselection """
        self.article.unselect_field(self.soustitre_field)

        self.assertNotIn(self.soustitre_field, self.article.selected_fields())
        self.assertNotIn(self.soustitre_field.uid, self.article.fields_list)

    def testSelectFieldInvalid(self):
        """ Testing optionnal field selection with invalid fields """
        with self.assertRaises(ValueError):
            self.personne.select_field(self.nom_field)
        with self.assertRaises(ValueError):
            self.personne.select_field(self.soustitre_field)


class TestTypeHierarchy(TypeTestCase):

    def testAddSuperior(self):
        """ Testing add_superior() """
        self.numero.add_superior(self.rubrique, EmNature.PARENT)

        self.assertIn(self.rubrique, self.numero.superiors()[EmNature.PARENT])
        self.assertIn(self.rubrique.uid, self.numero.superiors_list[EmNature.PARENT])
        self.assertIn(self.numero, self.rubrique.subordinates()[EmNature.PARENT])

        # add it twice, it should not be listed twice
        self.numero.add_superior(self.rubrique, EmNature.PARENT)
        self.assertEqual(1, len(self.numero.superiors()[EmNature.PARENT]))

    def testDelSuperior(self):
        """ Testing del_superior() """

        # rubrique should be a superior of article
        self.assertIn(self.rubrique, self.article.superiors()[EmNature.PARENT])
        # article should be in rubrique subordinates
        self.assertIn(self.article, self.rubrique.subordinates()[EmNature.PARENT])

        self.article.del_superior(self.rubrique, EmNature.PARENT)

        # article should not have EmNature.PARENT superior anymore
        with self.assertRaises(KeyError):
            self.article.superiors()[EmNature.PARENT]

        # article should not be in rubrique subordinates
        self.assertNotIn(self.article, self.rubrique.subordinates()[EmNature.PARENT])

        # but rubrique should still be a subordinate of itself
        self.assertIn(self.rubrique, self.rubrique.subordinates()[EmNature.PARENT])

        # test preservation of superiors of other nature

    def testBadHierarchy(self):
        """ testing bad use of hierarchy """

        # add a superior of different classtype
        with self.assertRaises(ValueError):
            self.numero.add_superior(self.personne, EmNature.PARENT)

        # add a superior with bad nature
        with self.assertRaises(ValueError):
            self.numero.add_superior(self.rubrique, EmNature.IDENTITY)

        # delete an invalid superior
        self.article.del_superior(self.numero, EmNature.PARENT)


class TestTypesMisc(TypeTestCase):

    def testFieldgroups(self):

        # should not send empty fieldgroups
        self.assertNotIn(self.couleur_group, self.article.fieldgroups())

        # add a field, fieldgroup should now appear
        self.article.select_field(self.couleur_field)
        self.assertIn(self.couleur_group, self.article.fieldgroups())

        # delete it, fieldgroup should disappear
        self.article.unselect_field(self.couleur_field)
        self.assertNotIn(self.couleur_group, self.article.fieldgroups())


class TestDeleteTypes(TypeTestCase):

    def testDeleteTypes(self):
        """ Testing EmType deletion """

        # should be okay to delete article
        article_id = self.article.uid
        self.assertTrue(self.me.delete_component(self.article.uid))

        # and it should not exist anymore
        self.assertFalse(self.me.component(article_id))
        # relations with other type should be deleted
        self.assertNotIn(self.article, self.rubrique.subordinates()[EmNature.PARENT])

        # rubrique has subordinates, should not be okay to delete
        self.assertFalse(self.me.delete_component(self.rubrique.uid))
