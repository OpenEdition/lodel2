import unittest
from unittest.mock import MagicMock, patch

from EditorialModel.model import Model
from EditorialModel.classes import EmClass
from EditorialModel.types import EmType
from EditorialModel.fieldgroups import EmFieldGroup
from EditorialModel.fields import EmField
from EditorialModel.fieldtypes.char import EmFieldChar
from EditorialModel.components import EmComponent
from Lodel.utils.mlstring import MlString


from EditorialModel.backend.json_backend import EmBackendJson
from EditorialModel.backend.dummy_backend import EmBackendDummy
from EditorialModel.migrationhandler.django import DjangoMigrationHandler
from EditorialModel.migrationhandler.dummy import DummyMigrationHandler

class TestModel(unittest.TestCase):

    def setUp(self):
        self.me = Model(EmBackendJson('EditorialModel/test/me.json'))

    def test_init(self):
        """ Instanciation test """
        model = Model(EmBackendJson('EditorialModel/test/me.json'))
        self.assertTrue(isinstance(model, Model))

        model = Model(EmBackendJson('EditorialModel/test/me.json'), migration_handler=DjangoMigrationHandler('LodelTestInstance', debug=False, dryrun=True))
        self.assertTrue(isinstance(model, Model))

    def test_bad_init(self):
        """ Test initialisation with bad arguments """
        for bad in [ None, int, EmBackendDummy, DummyMigrationHandler, 'foobar' ]:
            with self.assertRaises(TypeError, msg="Tried to instanciate a Model with a bad backend"):
                Model(bad)
        for bad in [ int, EmBackendDummy, DummyMigrationHandler, 'foobar' ]:
            with self.assertRaises(TypeError, msg="Tried to instanciate a Model with a migration_handler"):
                Model(EmBackendDummy(), bad)

    def test_components(self):
        """ Test components fetching """
        uid_l = list()
        for comp_class in [EmClass, EmType, EmField, EmFieldGroup]:
            comp_l = self.me.components(comp_class)
            #Testing types of returned components
            for component in comp_l:
                self.assertTrue(isinstance(component, comp_class), "Model.components method doesn't return EmComponent of the right type. Asked for {} but got {}".format(type(comp_class), type(component)))
                uid_l.append(component.uid)
        
        #Testing that we have fetched all the components
        for uid in self.me._components['uids']:
            self.assertIn(uid, uid_l, "Component with uid %d was not fetched"%uid)

        #Testing components method without parameters
        uid_l = [ comp.uid for comp in self.me.components() ]

        for uid in self.me._components['uids']:
            self.assertIn(uid, uid_l, "Component with uid %d was not fetched using me.components()"%uid)

        self.assertFalse(self.me.components(EmComponent))
        self.assertFalse(self.me.components(int))

    def test_component(self):
        """ Test component fetching by uid """
        #assert that __hash__, __eq__ and components() are corrects
        for comp in self.me.components():
            self.assertEqual(comp, self.me.component(comp.uid))

        for baduid in [-1, 0xffffff, "hello" ]:
            self.assertFalse(self.me.component(baduid))

    def test_sort_components(self):
        """ Test that Model.sort_components method actually sort components """
        # disordering an EmClass
        cl_l = self.me.components(EmClass)
        last_class = cl_l[0]
        last_class.rank = 10000
        self.me.sort_components(EmClass)
        self.assertEqual(self.me._components['EmClass'][-1].uid, last_class.uid, "The sort_components method doesn't really sort by rank")

    def test_new_uid(self):
        """ Test that model.new_uid return a new uniq uid """
        new_uid = self.me.new_uid()
        self.assertNotIn(new_uid, self.me._components['uids'].keys())

    def test_create_component_fails(self):
        """ Test the create_component method with invalid arguments """

        testDatas = {
            'name': 'FooBar',
            'classtype':'entity',
            'help_text': None,
            'string': None,
        }

        #Invalid uid
        used_uid = self.me.components()[0].uid
        for bad_uid in [ used_uid, -1, -1000, 'HelloWorld']:
            with self.assertRaises(ValueError, msg="The component was created but the given uid (%s) whas invalid (allready used, negative or WTF)"%bad_uid):
                self.me.create_component('EmClass', testDatas, uid = bad_uid)

        #Invalid component_type
        for bad_comp_name in ['EmComponent', 'EmFoobar', 'int', int]:
            with self.assertRaises(ValueError, msg="The create_component don't raise when an invalid classname (%s) is given as parameter"%bad_comp_name):
                self.me.create_component(bad_comp_name, testDatas)

        #Invalid rank
        for invalid_rank in [-1, 10000]:
            with self.assertRaises(ValueError, msg="A invalid rank (%s) was given"%invalid_rank):
                foodat = testDatas.copy()
                foodat['rank'] = invalid_rank
                self.me.create_component('EmClass', foodat)
        with self.assertRaises(TypeError, msg="A non integer rank was given"):
            foodat = testDatas.copy()
            foodat['rank'] = 'hello world'
            self.me.create_component('EmClass', foodat)

        #Invalid datas
        for invalid_datas in [ dict(), [1,2,3,4], ('hello', 'world') ]:
            with self.assertRaises(TypeError, msg="Invalid datas was given in parameters"):
                self.me.create_component('EmClass', invalid_datas)

    def test_create_components(self):
        """ Test the create_component method mocking the EmComponent constructors """
        
        params = {
            'EmClass' : {
                'cls' : EmClass,
                'cdats' : {
                    'name': 'FooClass',
                    'classtype':'entity',
                }
            },
            'EmType' : {
                'cls': EmType,
                'cdats' : {
                    'name' : 'FooType',
                    'class_id': self.me.components(EmClass)[0].uid,
                    'fields_list': [],
                }
            },
            'EmFieldGroup': {
                'cls': EmFieldGroup,
                'cdats' : {
                    'name' : 'FooFG',
                    'class_id': self.me.components(EmClass)[0].uid,
                },
            },
            'EmField': {
                'cls': EmFieldChar,
                'cdats': {
                    'name': 'FooField',
                    'fieldgroup_id': self.me.components(EmFieldGroup)[0].uid,
                    'fieldtype': 'char',
                    'max_length': 64,
                    'optional':True,
                    'internal': False,
                    'rel_field_id':None,
                    'icon': '0',
                    'nullable': False,
                    'uniq': True,
                }
            }
        }

        for n in params:
            tmpuid = self.me.new_uid()
            cdats = params[n]['cdats']
            cdats['string'] = MlString()
            cdats['help_text'] = MlString()
            with patch.object(params[n]['cls'], '__init__', return_value=None) as initmock:
                try:
                    self.me.create_component(n, params[n]['cdats'])
                except AttributeError: #Raises because the component is a MagicMock
                    pass
                cdats['uid'] = tmpuid
                cdats['model'] = self.me
                #Check that the component __init__ method was called with the good arguments
                initmock.assert_called_once_with(**cdats)

    def test_delete_component(self):
        """ Test the delete_component method """

        #Test that the delete_check() method is called
        for comp in self.me.components():
            with patch.object(comp.__class__, 'delete_check', return_value=False) as del_check_mock:
                ret = self.me.delete_component(comp.uid)
                del_check_mock.assert_called_once_with()
                #Check that when the delete_check() returns False de delete_component() too
                self.assertFalse(ret)

        #Using a new me for deletion test
        new_em = Model(EmBackendJson('EditorialModel/test/me.json'))
        for comp in new_em.components():
            cuid = comp.uid
            cname = new_em.name_from_emclass(comp.__class__)
            #Simulate that the delete_check() method returns True
            with patch.object(comp.__class__, 'delete_check', return_value=True) as del_check_mock:
                ret = new_em.delete_component(cuid)
                self.assertTrue(ret)
                self.assertNotIn(cuid, new_em._components['uids'])
                self.assertNotIn(comp, new_em._components[cname])
    
    def test_set_backend(self):
        """ Test the set_backend method """

        for backend in [ EmBackendJson('EditorialModel/test/me.json'), EmBackendDummy() ]:
            self.me.set_backend(backend)
            self.assertEqual(self.me.backend, backend)

        for bad_backend in [None, 'wow', int, EmBackendJson ]:
            with self.assertRaises(TypeError, msg="But bad argument (%s %s) was given"%(type(bad_backend),bad_backend)):
                self.me.set_backend(bad_backend)
    ##
    # @todo Test selected fields application
    # @todo Test types hierarchy application
    def test_migrate_handler(self):
        """ Test that the migrate_handler() method create component in a good order """
        
        #Testing component creation
        with patch.object(Model, 'create_component', return_value=None) as create_mock:
            try:
                self.me.migrate_handler(None)
            except AttributeError: #Raises because of the mock
                pass
            order_comp = ['EmClass', 'EmType', 'EmFieldGroup', 'EmField'] #Excpected creation order
            cur_comp = 0
            for mcall in create_mock.mock_calls:
                #Testing EmComponent order of creation
                while order_comp[cur_comp] != mcall[1][0]:
                    cur_comp +=1
                    if cur_comp >= len(order_comp):
                        self.assertTrue(False, 'The order of create_component() calls was not respected by migrate_handler() methods');

                #Testing uid
                comp = self.me.component(mcall[1][2])
                ctype = self.me.name_from_emclass(comp.__class__)
                self.assertEqual(mcall[1][0], ctype, "A component was created using a uid belonging to another component type")
                #Testing arguments of create_component
                comp_dump = comp.attr_dump()
                if 'fields_list' in comp_dump and comp_dump['fields_list']:
                    del(comp_dump['fields_list'])
                if 'superiors_list' in comp_dump and comp_dump['superiors_list']:
                    del(comp_dump['superiors_list'])

                self.assertEqual(mcall[1][1], comp_dump)

        #Now testing the select type application
        pass
        #Now testing the type hierarchy
        pass

        #Now testing the hashes
        with patch.object(DummyMigrationHandler, 'register_change', return_value=None) as mh_mock:
            new_me = self.me.migrate_handler(DummyMigrationHandler())
            last_call = mh_mock.mock_calls[-1]
            self.assertEqual(hash(last_call[1][0]), hash(self.me))


    def test_hash(self):
        """ Test that __hash__ and __eq__ work properly on models """
        me1 = Model(EmBackendJson('EditorialModel/test/me.json'))
        me2 = Model(EmBackendJson('EditorialModel/test/me.json'), migration_handler=DjangoMigrationHandler('LodelTestInstance', debug=False, dryrun=True))

        self.assertEqual(hash(me1), hash(me2), "When instanciate from the same backend & file but with another migration handler the hashes differs")
        self.assertTrue(me1.__eq__(me2))

        cl_l = me1.classes()
        cl_l[0].modify_rank(1)

        self.assertNotEqual(hash(me1), hash(me2), "After a class rank modification the hashes are the same")
        self.assertFalse(me1.__eq__(me2))

        cl_l = me2.classes()
        cl_l[0].modify_rank(1)

        self.assertEqual(hash(me1), hash(me2), "After doing sames modifications in the two models the hashes differs")
        self.assertTrue(me1.__eq__(me2))

    def test_compclass_getter(self):
        """ Test the Model methods that handles name <-> EmComponent conversion """
        for classname in [ 'EmField', 'EmClass', 'EmFieldGroup', 'EmType' ]:
            cls = Model.emclass_from_name(classname)
            self.assertNotEqual(cls, False, "emclass_from_name return False when '%s' given as parameter"%classname)
            self.assertEqual(cls.__name__, classname)

        for classname in ['EmComponent', 'EmFoobar' ]:
            self.assertFalse( Model.emclass_from_name(classname))

        for comp_cls in [EmClass, EmFieldGroup, EmType]:
            self.assertEqual(Model.name_from_emclass(comp_cls), comp_cls.__name__)
        for comp in self.me.components(EmField):
            self.assertEqual(Model.name_from_emclass(comp.__class__), 'EmField')

        for cls in [EmComponent, int, str]:
            self.assertFalse(Model.name_from_emclass(cls))


