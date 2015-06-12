import os
import datetime
import time
import logging
import json

#from django.test import TestCase
from django.conf import settings

from unittest import TestCase
import unittest

from EditorialModel.components import EmComponent, EmComponentNotExistError
from Lodel.utils.mlstring import MlString

from Database.sqlsetup import SQLSetup
from Database.sqlwrapper import SqlWrapper
from Database import sqlutils
import sqlalchemy as sqla

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

#A dummy EmComponent child class use to make tests
class EmTestComp(EmComponent):
    table = 'ttest'
    def __init__(self, ion):
        super(EmTestComp, self).__init__(ion)

class ComponentTestCase(TestCase):

    # ############# # 
    #  TESTS SETUP  #
    # ############# #
    @classmethod
    def setUpClass(cls):
        #Overwritting db confs to make tests
        settings.LODEL2SQLWRAPPER = {
            'default': {
                'ENGINE': 'sqlite',
                'NAME': '/tmp/testdb.sqlite'
            }
        }
        
        """
            'default': {
                'ENGINE': 'mysql',
                'NAME': 'lodel2crea',
                'USER': 'lodel',
                'PASSWORD': 'bruno',
            },
        """
        #Disable logging but CRITICAL
        logging.basicConfig(level=logging.CRITICAL)

        #testDB setup
        #   TODO May be slow
        sqls = SQLSetup()
        tables = sqls.get_schema()
        ttest = {   'name':'ttest',
                    'columns':  [
                        {"name":"uid",          "type":"INTEGER", "extra":{"foreignkey":"uids.uid", "nullable":False, "primarykey":True}},
                        {"name":"name",         "type":"VARCHAR(50)", "extra":{"nullable":False, "unique":True}},
                        {"name":"string",       "type":"TEXT"},
                        {"name":"help",         "type":"TEXT"},
                        {"name":"rank",         "type":"INTEGER"},
                        {"name":"date_update",  "type":"DATETIME"},
                        {"name":"date_create",  "type":"DATETIME"}
                    ]
                }
        tables.append(ttest)

        
        #cls.db = SqlWrapper(read_db='default', write_db = 'default', alchemy_logs=True)
        cls.db = SqlWrapper(read_db='default', write_db = 'default', alchemy_logs=False)
        cls.tables = tables

    @property
    def db(self):
        return self.__class__.db
    @property
    def tables(self):
        return self.__class__.tables

    def setUp(self):
        # Db RAZ
        self.db.dropAll()
        # Db schema creation
        self.db.createAllFromConf(self.tables);
        self.dber = self.db.r_engine
        self.dbew = self.db.w_engine
        
        # Test Em creation
        conn = self.dber.connect()
        test_table = sqla.Table(EmTestComp.table, sqlutils.meta(self.dber))
        uids_table = sqla.Table('uids', sqlutils.meta(self.dber))
        tuid = [ 1, 2, 3 , 42, 84 , 1025 ]

        #Creating uid for the EmTestComp
        for uid in tuid:
            req = uids_table.insert(values={'uid':uid, 'table': EmTestComp.table })
            conn.execute(req)

        # WARNING !!! Rank has to be ordened and incremented by one for the modify_rank tests
        self.test_values = [
            { 'uid': tuid[0], 'name': 'test', 'string': '{"fr":"testcomp"}', 'help': '{"en":"help test", "fr":"test help"}', 'rank': 0},
            { 'uid': tuid[1], 'name': 'test-em_comp', 'string': '{"fr":"Super test comp"}', 'help': '{}', 'rank': 1},
            { 'uid': tuid[2], 'name': 'test2', 'string': '{}', 'help': '{}', 'rank': 2},
            { 'uid': tuid[3], 'name': 'foo', 'string': '{"foo":"bar"}', 'help': '{"foo":"foobar"}', 'rank': 3},
            { 'uid': tuid[4], 'name': '123', 'string': '{"num":"456"}', 'help': '{"num":"4242"}', 'rank': 4},
            { 'uid': tuid[5], 'name': 'name', 'string': '{}', 'help': '{}', 'rank': 5},
        ]

        for i in range(len(self.test_values)):
            self.test_values[i]['date_create'] = datetime.datetime.utcnow()
            self.test_values[i]['date_update'] = datetime.datetime.utcnow()
            

        req = test_table.insert(values=self.test_values)
        conn.execute(req)
        conn.close()

        footable = sqla.Table('em_class', sqlutils.meta(self.dber))
        foocol = footable.c.date_update
        pass
    
    def check_equals(self, excepted_val, test_comp, check_date=True):
        """ This function check that a EmTestComp has excepted_val for values """
        val = excepted_val
        self.assertIsInstance(test_comp, EmTestComp)
        for vname in val:
            if vname in ['string', 'help']: #Special test for mlStrings
                #MlString comparison
                vml = json.loads(val[vname])
                for vn in vml:
                    self.assertEqual(vml[vn], getattr(test_comp, vname).get(vn))
            elif vname in ['date_create', 'date_update']:
                # Datetime comparison
                if check_date:
                    self.assertEqualDatetime(val[vname], getattr(test_comp, vname))
            else:
                if vname == 'uid':
                    prop = 'id'
                else:
                    prop = vname
                self.assertEqual(getattr(test_comp, prop), val[vname], "Inconsistency for "+prop+" property")
        pass

    def assertEqualDatetime(self, d1,d2, msg=""):
        """ Compare a date from the database with a datetime (that have microsecs, in db we dont have microsecs) """
        self.assertTrue( d1.year == d2.year and d1.month == d2.month and d1.day == d2.day and d1.hour == d2.hour and d1.minute == d2.minute and d1.second == d2.second, msg+" Error the two dates differs : '"+str(d1)+"' '"+str(d2)+"'")

    def assertEqualMlString(self, ms1, ms2, msg=""):
        """ Compare two MlStrings """
        ms1t = ms1.translations
        ms2t = ms2.translations
        self.assertEqual(set(name for name in ms1t), set(name for name in ms2t), msg+" The two MlString hasn't the same lang list")
        for n in ms1t:
            self.assertEqual(ms1t[n], ms2t[n])

    # ############# #
    #  TESTS BEGIN  #
    # ############# #

    #
    #   EmComponent.newUid
    #
    def test_newuid(self):
        """ Test valid calls for newUid method """
        for _ in range(10):
            nuid = EmTestComp.newUid()
        
            conn = self.dber.connect()
            tuid = sqla.Table('uids', sqlutils.meta(self.dber))
            req = sqla.select([tuid]).where(tuid.c.uid == nuid)
            rep = conn.execute(req)
            res = rep.fetchall()
        
            self.assertEqual(len(res), 1)
            res = res[0]
            self.assertEqual(res.uid, nuid)
            self.assertEqual(res.table, EmTestComp.table)
        pass

    def test_newuid_abstract(self):
        """ Test not valit call for newUid method """
        with self.assertRaises(NotImplementedError):
            EmComponent.newUid()
        pass
    #
    #   EmComponent.__init__
    #
    def test_component_abstract_init(self):
        """ Test not valid call (from EmComponent) of __init__ """
        with self.assertRaises(EnvironmentError):
            test_comp = EmComponent(2)
        with self.assertRaises(EnvironmentError):
            test_comp = EmComponent('name')
        pass


    def test_component_init_not_exist(self):
        """ Test __init__ with non existing objects """
        with self.assertRaises(EmComponentNotExistError):
            test_comp = EmTestComp('not_exist')

        # TODO this assertion depends of the EmComponent behavior when instanciate with an ID
        #with self.assertRaises(EmComponentNotExistError):
        #    test_comp = EmTestComp(4096)

        pass

    def test_component_init_uid(self):
        """ Test __init__ with numerical ID """
        for val in self.test_values:
            test_comp = EmTestComp(val['uid'])
            self.assertIsInstance(test_comp, EmTestComp)
            self.assertEqual(test_comp.id, val['uid'])
        pass

    def test_component_init_name(self):
        """ Test __init__ with names """
        for val in self.test_values:
            test_comp = EmTestComp(val['name'])
            self.check_equals(val, test_comp)
        pass

    def test_component_init_badargs(self):
        for badarg in [ print, json, [], [1,2,3,4,5,6], {'hello': 'world'} ]:
            with self.assertRaises(TypeError):
                EmTestComp(badarg)
        pass

    #
    #   EmComponent.save
    #

    def _savecheck(self, test_comp, newval):
        """ Utility function for test_component_save_namechange """
        test_comp2 = EmTestComp(newval['name'])
        
        #Check if properties other than date are equals in the instance fetched from Db
        self.check_equals(newval, test_comp2, check_date=False)

        #Check if the date_update has been updated
        self.assertTrue(newval['date_update'] < test_comp2.date_update, "The updated date_update is more in past than its previous value : old date : '"+str(newval['date_update'])+"' new date '"+str(test_comp2.date_update)+"'")

        #Check if the date_create didn't change
        self.assertEqualDatetime(newval['date_create'], test_comp2.date_create)

        #Check if the instance fecthed from Db and the one used to call save have the same properties
        for prop in ['name', 'help', 'string', 'date_update', 'date_create', 'rank' ]:
            if prop in ['string', 'help']:
                assertion = self.assertEqualMlString
            elif prop in ['date_update', 'date_create']:
                assertion = self.assertEqualDatetime
            else:
                assertion = self.assertEqual

            assertion(getattr(test_comp, prop), getattr(test_comp2, prop), "Save don't propagate modification properly. The '"+prop+"' property differs between the modified instance and a new one fetch from Db : ")
        pass

    def test_component_save_setattr(self):
        """ Checking save method after different changes using setattr """

        val = self.test_values[0] #The row we will modify

        test_comp = EmTestComp(val['name'])
        self.check_equals(val, test_comp)

        newval = val.copy()

        time.sleep(2) # We have to sleep 2 secs here, so the update_date will be at least 2 secs more than newval['date_update']

        #name change
        newval['name'] = test_comp.name = 'newname'
        test_comp.save({})
        self._savecheck(test_comp, newval)

        #help change
        newval['help'] = '{"fr": "help fr", "en":"help en", "es":"help es"}'
        test_comp.help = MlString.load(newval['help'])
        test_comp.save()
        self._savecheck(test_comp, newval)
        
        #string change
        newval['string'] = '{"fr": "string fr", "en":"string en", "es":"string es"}'
        test_comp.string = MlString.load(newval['string'])
        test_comp.save()
        self._savecheck(test_comp, newval)

        #no change
        test_comp.save()
        self._savecheck(test_comp, newval)

        #change all
        newval['name'] = test_comp.name = 'newnewname'
        newval['help'] = '{"fr": "help fra", "en":"help eng", "es":"help esp"}'
        newval['string'] = '{"fr": "string FR", "en":"string EN", "es":"string ES", "foolang":"foofoobar"}'
        test_comp.save()
        self._savecheck(test_comp, newval)
        pass

    @unittest.skip("Soon we will not use anymore the values argument of the savec method")
    def test_component_save(self):
        """ Checking save method after different changes using values arg of save method """
        val = self.test_values[0]
        test_comp = EmTestComp(val['name'])
        self.check_equals(val, test_comp)

        save_args = [
            { 'name': 'foonewname' },
            { 'name': 'foo new name'},
            { 'help': '{"fr": "strhelp fr", "en":"strhelp en", "es":"strhelp es"}'},
            { 'string': '{"fr": "helpstr fr", "en":"helpstr en", "es":"helpstr es"}'},
            { 'name': 'oldname', 'help':'{"fr": "help fra", "en":"help eng", "es":"help esp"}', 'string':'{"fr": "string FR", "en":"string EN", "es":"string ES", "foolang":"foofoobar"}'},
            { 'help': '{}', 'string':'{}'},
        ]
        for values in save_args:
            for vname in values:
                val[vname] = values[vname]

            v = values.copy()
            #WARNING : v is set by save
            test_comp.save(v)
            
            print(val,"\n" ,values)
            self._savecheck(test_comp, val)

    def test_component_save_illegalchanges(self):
        """ checking that the save method forbids some changes """
        val = self.test_values[1]

        changes = { 'date_create': datetime.datetime(1982,4,2,13,37), 'date_update': datetime.datetime(1982,4,2,22,43), 'rank': 42 }

        for prop in changes:
            test_comp = EmTestComp(val['name'])
            self.check_equals(val, test_comp)
            
            setattr(test_comp, prop, changes[prop])
            test_comp.save({})

            test_comp2 = EmTestComp(val['name'])

            if prop in ['date_create', 'date_update']:
                assertion = self.assertEqualDatetime
            else: #rank
                assertion = self.assertEqual

            assertion(getattr(test_comp,prop), val[prop], "When using setattr the "+prop+" of a component is set : ")
            assertion(getattr(test_comp2, prop), val[prop], "When using setattr and save the "+prop+" of a loaded component is set : ")

            # The code block commented bellow uses the values argument of the save method.
            # soon this argument will not being used anymore
            """
            test_comp = EmTestComp(val['name'])
            self.check_equals(val, test_comp)
            test_comp.save({ prop: changes['prop'] })

            test_comp2 = EmTestComp(val['name'])
            self.assertEqualDatetime(test_comp.date_create, val[prop], "The "+prop+" of the component instance has been changed")
            self.assertEqualDatetime(test_comp2.date_create, val[prop], "When loaded the "+prop+" has been changed")
            """
        pass
    
    #
    # EmComponent.modify_rank
    #
    def test_modify_rank_absolute(self):
        """ Testing modify_rank with absolute rank """
        
        names = [ v['name'] for v in self.test_values ]
        nmax = len(names)-1
        
        #moving first to 3
        test_comp = EmTestComp(names[0])

        test_comp.modify_rank(3, '=')
        self.assertEqual(test_comp.rank, 3)

        for i in range(1,4):
            test_comp = EmTestComp(names[i])
            self.assertEqual(test_comp.rank, i-1, "Excepted rank was '"+str(i-1)+"' but found '"+str(test_comp.rank)+"'")

        for i in [4,nmax]:
            test_comp = EmTestComp(names[i])
            self.assertEqual(test_comp.rank, i, "Rank wasn't excepted to change, but : previous value was '"+str(i)+"' current value is '"+str(test_comp.rank)+"'")

        #undoing last rank change
        test_comp = EmTestComp(names[0])
        test_comp.modify_rank(0,'=')
        self.assertEqual(test_comp.rank, 0)

        #moving last to 2
        test_comp = EmTestComp(names[nmax])

        test_comp.modify_rank(2, '=')
        
        for i in [0,1]:
            test_comp = EmTestComp(names[i])
            self.assertEqual(test_comp.rank, i)
        for i in range(3,nmax+1):
            test_comp = EmTestComp(names[i])
            self.assertEqual(testc_omp.rank, i+1)

        #undoing last rank change
        test_comp = EmTestComp(names[nmax])
        test_comp.modify_rank(nmax,'=')
        self.assertEqual(test_comp.rank, nmax)
        
        #Checking that we are in original state again
        for i,name in enumerate(names):
            test_comp = EmTestComp(name)
            self.assertEqual(test_comp.rank, i, "Excepted rank was '"+str(i-1)+"' but found '"+str(test_comp.rank)+"'")
        
        #Inverting the list
        for i,name in enumerate(names):
            test_comp = EmTestComp(name)
            test_comp.modify_rank(0,'=')
            self.assertEqual(test_comp.rank, 0)
            for j in range(0,i+1):
                test_comp = EmTestComp(names[j])
                self.assertEqual(test_comp.rank, i-j)
            for j in range(i+1,nmax+1):
                test_comp = EmTestComp(names[j])
                self.assertEqual(test_comp.rank, j)

        #Not inverting the list
        for i in range(nmax,-1,-1):
            test_comp = EmTestComp(name)
            test_comp.modify_rank(nmax,'=')
            self.assertEqual(test_comp.rank, nmax)
            for j in range(i,nmax+1):
                test_comp = EmTestComp(names[j])
                self.assertEqual(test_comp.rank, nmax-(j-i))
            for j in range(0,i):
                test_comp = EmTestComp(names[j])
                self.assertEqual(test_comp.rank, i-j-1)

        pass

    def test_modify_rank_relative(self):
        """ Testing modify_rank with relative rank modifier """
        names = [ v['name'] for v in self.test_values ]
        nmax = len(names)-1
        
        test_comp = EmTestComp(names[0])
        for i in range(1,nmax):
            test_comp.modify_rank(i,'+')
            self.assertEqual(test_comp.rank, i, "The instance on wich we applied the modify_rank doesn't have expected rank : expected '"+str(i)+"' but got '"+str(test_comp.rank)+"'")
            test_comp2 = EmTestComp(names[0])
            self.assertEqual(test_comp.rank, i, "The instance fetched in Db does'n't have expected rank : expected '"+str(i)+"' but got '"+str(test_comp.rank)+"'")

            for j in range(1,i+1):
                test_comp2 = EmTestComp(names[j])
                self.assertEqual(test_comp2.rank, j-1)
            for j in range(i+1,nmax+1):
                test_comp2 = EmTestComp(names[j])
                self.assertEqual(test_comp2.rank, j)

            test_comp.modify_rank(i,'-')
            self.assertEqual(test_comp.rank, 0, "The instance on wich we applied the modify_rank -"+str(i)+" doesn't have excepted rank : excepted '0' but got '"+str(test_comp.rank)+"'")
            test_comp2 = EmTestComp(names[0])
            self.assertEqual(test_comp.rank, i, "The instance fetched in Db does'n't have expected rank : expected '0' but got '"+str(test_comp.rank)+"'")

            for j in range(1,nmax+1):
                test_comp2 = EmTestComp(names[j])
                self.assertEqual(test_comp2.rank, j)

        test_comp = EmTestComp(names[3])
        test_comp.modify_rank('2','+')
        self.assertEqual(test_comp.rank, 5)
        tc2 = EmTestComp(names[3])
        self.assertEqual(tc2.rank,5)
        for i in [4,5]:
            tc2 = EmTestComp(names[i])
            self.assertEqual(tc2.rank, i-1)
        for i in range(0,3):
            tc2 = EmTestComp(names[i])
            self.assertEqual(tc2.rank, i)

        test_comp.modify_rank('2', '-')
        self.assertEqual(test_comp.rank, 3)
        for i in range(0,6):
            tc2 = EmTestComp(names[i])
            self.assertEqual(tc2.rank, i)

        pass

    def test_modify_rank_badargs(self):
        """ Testing modify_rank with bad arguments """
        names = [ v['name'] for v in self.test_values ]
        tc = EmTestComp(names[3])
        
        badargs = [
            #Bad types
            (('0','+'), TypeError),
            ((0, 43), TypeError),
            ((print, '='), TypeError),
            ((3, print), TypeError),
            ((0.0, '='), TypeError),
            
            #Bad new_rank
            ((0,'+'), ValueError),
            ((0,'-'), ValueError),
            ((-1, '+'), ValueError),
            ((-1,'-'), ValueError),
            ((-1, '='), ValueError),
            ((-1,), ValueError),
            
            #Bad sign
            ((2, 'a'), ValueError),
            ((1, '=='), ValueError),
            ((1, '+-'), ValueError),
            ((1, 'Hello world !'), ValueError),
            
            #Out of bounds
            ((42*10**9), '+', ValueError),
            ((-42*10**9), '+', ValueError),
            ((len(names), '+'), ValueError),
            ((len(names), '-'), ValueError),
            ((len(names), '='), ValueError),
            ((4, '-'), ValueError),
            ((3, '+'), ValueError),
        ]

        for (args, err) in badargs:
            with self.assertRaises(TypeError, "Bad arguments supplied : "+str(args)+" but no error raised"):
                test_comp.modify_rank(*args)
            self.assertEqual(tc.rank, 3, "The function raises an error but modify the rank")
        pass


