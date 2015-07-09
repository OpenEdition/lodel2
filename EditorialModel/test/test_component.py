import os
import datetime
import time
import logging
import json
import shutil

#from django.test import TestCase
from django.conf import settings

from unittest import TestCase
import unittest

from EditorialModel.classes import EmClass
from EditorialModel.classtypes import EmClassType

from EditorialModel.components import EmComponent, EmComponentNotExistError, EmComponentExistError
import EditorialModel.fieldtypes as ftypes

from EditorialModel.test.utils import *

from Lodel.utils.mlstring import MlString

from Database import sqlutils
from Database import sqlsetup
import sqlalchemy as sqla


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lodel.settings")

TEST_COMPONENT_DBNAME = 'test_em_component_db.sqlite'

#=#############=# 
#  TESTS SETUP  #
#=#############=#

def setUpModule():
    """ This function is run once for this module.
        
        The goal are to overwrtie Db configs, and prepare objects for test_case initialisation
    """
    cleanDb(TEST_COMPONENT_DBNAME)

    setDbConf(TEST_COMPONENT_DBNAME)
    #Disable logging but CRITICAL
    logging.basicConfig(level=logging.CRITICAL)

    #testDB setup
    tables = sqlsetup.get_schema()
    ttest = {   'name':'ttest',
                'columns':  [
                    {"name":"uid",          "type":"INTEGER", "extra":{"foreignkey":"uids.uid", "nullable":False, "primarykey":True}},
                    {"name":"name",         "type":"VARCHAR(50)", "extra":{"nullable":False, "unique":True}},
                    {"name":"string",       "type":"TEXT"},
                    {"name":"help",         "type":"TEXT"},
                    {"name":"rank",         "type":"INTEGER"},
                    {"name":"rank_fam",    "type":"VARCHAR(1)"},
                    {"name":"date_update",  "type":"DATETIME"},
                    {"name":"date_create",  "type":"DATETIME"}
                ]
            }
    tables.append(ttest)

    globals()['tables'] = tables

    #Creating db structure

    initTestDb(TEST_COMPONENT_DBNAME)
    setDbConf(TEST_COMPONENT_DBNAME)

    sqlsetup.init_db('default', False, tables)   

    dbe = sqlutils.get_engine('default')

    # Insertion of testings datas
    conn = dbe.connect()
    test_table = sqla.Table(EmTestComp.table, sqlutils.meta(dbe))
    uids_table = sqla.Table('uids', sqlutils.meta(dbe))

    #Creating uid for the EmTestComp
    for v in ComponentTestCase.test_values:
        uid = v['uid']
        req = uids_table.insert(values={'uid':uid, 'table': EmTestComp.table })
        conn.execute(req)

    # WARNING !!! Rank has to be ordened and incremented by one for the modify_rank tests

    for i in range(len(ComponentTestCase.test_values)):
        ComponentTestCase.test_values[i]['date_create'] = datetime.datetime.utcnow()
        ComponentTestCase.test_values[i]['date_update'] = datetime.datetime.utcnow()
        ComponentTestCase.test_values[i]['rank_fam'] = '1'
        

    req = test_table.insert(values=ComponentTestCase.test_values)
    conn.execute(req)
    conn.close()

    saveDbState(TEST_COMPONENT_DBNAME)

    logging.getLogger().setLevel(logging.CRITICAL)
    pass

def tearDownModule():
    cleanDb(TEST_COMPONENT_DBNAME)
    """
    try:
        os.unlink(TEST_COMPONENT_DBNAME)
    except:pass
    try:
        os.unlink(TEST_COMPONENT_DBNAME+'_bck')
    except:pass
    """

#A dummy EmComponent child class use to make tests
class EmTestComp(EmComponent):
    table = 'ttest'
    ranked_in = 'rank_fam'
    _fields = [('rank_fam', ftypes.EmField_char)]

# The parent class of all other test cases for component
# It defines a SetUp function and some utility functions for EmComponent tests
class ComponentTestCase(TestCase):

    test_values = [
        { 'uid': 1, 'name': 'test', 'string': '{"fr":"testcomp"}', 'help': '{"en":"help test", "fr":"test help"}', 'rank': 0},
        { 'uid': 2, 'name': 'test-em_comp', 'string': '{"fr":"Super test comp"}', 'help': '{}', 'rank': 1},
        { 'uid': 3, 'name': 'test2', 'string': '{}', 'help': '{}', 'rank': 2},
        { 'uid': 42, 'name': 'foo', 'string': '{"foo":"bar"}', 'help': '{"foo":"foobar"}', 'rank': 3},
        { 'uid': 84, 'name': '123', 'string': '{"num":"456"}', 'help': '{"num":"4242"}', 'rank': 4},
        { 'uid': 1025, 'name': 'name', 'string': '{}', 'help': '{}', 'rank': 5},
    ]

    @property
    def tables(self):
        return globals()['tables']
    
    def setUp(self):
        self.dber = sqlutils.get_engine('default')
        self.test_values = self.__class__.test_values
        #Db RAZ
        #shutil.copyfile(TEST_COMPONENT_DBNAME+'_bck', globals()['component_test_dbfilename'])
        restoreDbState(TEST_COMPONENT_DBNAME)
        pass
    
    def check_equals(self, excepted_val, test_comp, check_date=True, msg=''):
        """ This function check that a EmTestComp has excepted_val for values """
        val = excepted_val
        self.assertIsInstance(test_comp, EmTestComp, msg)
        for vname in val:
            if vname in ['string', 'help']: #Special test for mlStrings
                #MlString comparison
                vml = json.loads(val[vname])
                for vn in vml:
                    self.assertEqual(vml[vn], getattr(test_comp, vname).get(vn), msg)
            elif vname in ['date_create', 'date_update']:
                # Datetime comparison
                if check_date:
                    self.assertEqualDatetime(val[vname], getattr(test_comp, vname), vname+" assertion error : "+msg)
            else:
                prop = vname
                self.assertEqual(getattr(test_comp, prop), val[vname], msg+"Inconsistency for "+prop+" property")
        pass

    def assertEqualDatetime(self, d1,d2, msg=""):
        """ Compare a date from the database with a datetime (that have microsecs, in db we dont have microsecs) """
        self.assertTrue(    d1.year == d2.year
                            and d1.month == d2.month
                            and d1.day == d2.day
                            and d1.hour == d2.hour
                            and d1.minute == d2.minute
                            and d1.second == d2.second, msg+" Error the two dates differs : '"+str(d1)+"' '"+str(d2)+"'")

    def assertEqualMlString(self, ms1, ms2, msg=""):
        """ Compare two MlStrings """
        ms1t = ms1.translations
        ms2t = ms2.translations
        self.assertEqual(set(name for name in ms1t), set(name for name in ms2t), msg+" The two MlString hasn't the same lang list")
        for n in ms1t:
            self.assertEqual(ms1t[n], ms2t[n])

    def run(self, result=None):
        super(ComponentTestCase, self).run(result)

#=#############=#
#  TESTS BEGIN  #
#=#############=#
       
#===========================#
#   EmComponent.__init__    #
#===========================#
class TestInit(ComponentTestCase):

    def test_component_abstract_init(self):
        """ Test not valid call (from EmComponent) of __init__ """
        with self.assertRaises(NotImplementedError):
            test_comp = EmComponent(2)
        with self.assertRaises(NotImplementedError):
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
            self.assertEqual(test_comp.uid, val['uid'])
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

#=======================#
#   EmComponent.new_uid  #
#=======================#
class TestUid(ComponentTestCase):

    
    def test_newuid(self):
        """ Test valid calls for new_uid method """
        for _ in range(10):
            nuid = EmTestComp.new_uid(self.dber)
        
            conn = self.dber.connect()
            tuid = sqla.Table('uids', sqlutils.meta(self.dber))
            req = sqla.select([tuid]).where(tuid.c.uid == nuid)
            rep = conn.execute(req)
            res = rep.fetchall()
        
            self.assertEqual(len(res), 1, "Error when selecting : mutliple rows returned for 1 UID")
            res = res[0]
            self.assertEqual(res.uid, nuid, "Selected UID didn't match created uid")
            self.assertEqual(res.table, EmTestComp.table, "Table not match with class table : expected '"+res.table+"' but got '"+EmTestComp.table+"'")
        pass
    
    def test_newuid_abstract(self):
        """ Test not valit call for new_uid method """
        with self.assertRaises(NotImplementedError):
            EmComponent.new_uid(self.dber)
        pass
        
#=======================#
#   EmComponent.save    #
#=======================#
class TestSave(ComponentTestCase):


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
            elif prop == 'date_create':
                assertion = self.assertEqualDatetime
            elif prop == 'date_update':
                assertion = self.assertLess
            else:
                assertion = self.assertEqual

            assertion(getattr(test_comp, prop), getattr(test_comp2, prop), "Save don't propagate modification properly. The '"+prop+"' property hasn't the exepted value in instance fetched from Db : ")
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
        test_comp.save()
        self._savecheck(test_comp, newval)
        self.assertTrue(True)

        #help change
        newval['help'] = '{"fr": "help fr", "en":"help en", "es":"help es"}'
        test_comp.help = MlString.load(newval['help'])
        test_comp.save()
        self._savecheck(test_comp, newval)
        self.assertTrue(True)
    
        #string change
        newval['string'] = '{"fr": "string fr", "en":"string en", "es":"string es"}'
        test_comp.string = MlString.load(newval['string'])
        test_comp.save()
        self._savecheck(test_comp, newval)
        self.assertTrue(True)

        #no change
        test_comp.save()
        self._savecheck(test_comp, newval)
        self.assertTrue(True)

        #change all
        test_comp.name = newval['name'] = test_comp.name = 'newnewname'
        newval['help'] = '{"fr": "help fra", "en":"help eng", "es":"help esp"}'
        test_comp.help = MlString.load(newval['help'])
        newval['string'] = '{"fr": "string FR", "en":"string EN", "es":"string ES", "foolang":"foofoobar"}'
        test_comp.string = MlString.load(newval['string'])

        test_comp.save()
        self._savecheck(test_comp, newval)
        self.assertTrue(True)

        pass

    def test_component_save_illegalchanges(self):
        """ checking that the save method forbids some changes """
        val = self.test_values[1]

        changes = { 'date_create': datetime.datetime(1982,4,2,13,37), 'date_update': datetime.datetime(1982,4,2,22,43), 'rank': 42 }

        for prop in changes:
            test_comp = EmTestComp(val['name'])
            self.check_equals(val, test_comp, False)
            
            with self.assertRaises(TypeError):
                setattr(test_comp, prop, changes[prop])
            test_comp.save()

            test_comp2 = EmTestComp(val['name'])

            if prop  == 'date_create':
                assertion = self.assertEqualDatetime
            elif prop == 'date_update':
                continue
            else: #rank
                assertion = self.assertEqual

            assertion(getattr(test_comp,prop), val[prop], "When using setattr the "+prop+" of a component is set : ")
            assertion(getattr(test_comp2, prop), val[prop], "When using setattr and save the "+prop+" of a loaded component is set : ")
        pass

#====================#
# EmComponent.create #
#====================#
class TestCreate(ComponentTestCase):
    
    def test_create(self):
        """Testing EmComponent.create()"""
        vals = {'name': 'created1', 'rank_fam': 'f', 'string': '{"fr":"testcomp"}', 'help': '{"en":"help test", "fr":"test help"}'}
        tc = EmTestComp.create(**vals)
        self.check_equals(vals, tc, "The created EmTestComp hasn't the good properties values")
        tcdb = EmTestComp('created1')
        self.check_equals(vals, tc, "When fetched from Db the created EmTestComp hasn't the good properties values")
    
        # This test assume that string and help has default values
        vals = { 'name': 'created2', 'rank_fam': 'f' }
        tc = EmTestComp.create(**vals)
        self.check_equals(vals, tc, "The created EmTestComp hasn't the good properties values")
        tcdb = EmTestComp('created1')
        self.check_equals(vals, tc, "When fetched from Db the created EmTestComp hasn't the good properties values")
        pass

    def test_create_badargs(self):
        """Testing EmComponent.create() with bad arguments"""
        with self.assertRaises(TypeError, msg="But given a function as argument"):
            tc = EmTestComp.create(print)
        with self.assertRaises(TypeError, msg="But values contains date_create and date_update"):
            vals = { 'name': 'created1', 'rank_fam': 'f', 'string': '{"fr":"testcomp"}', 'help': '{"en" :"help test", "fr":"test help"}', 'rank': 6, 'date_create': 0 , 'date_update': 0 }
            tc = EmTestComp.create(**vals)

        with self.assertRaises(TypeError, msg="But no name was given"):
            vals = { 'rank_fam': 'f', 'string': '{"fr":"testcomp"}', 'help': '{"en" :"help test", "fr":"test help"}', 'rank': 6, 'date_create': 0 , 'date_update': 0 }
            tc = EmTestComp.create(**vals)
        with self.assertRaises(TypeError, msg="But no rank_fam was given"):
            vals = { 'name': 'created1', 'string': '{"fr":"testcomp"}', 'help': '{"en" :"help test", "fr":"test help"}', 'rank': 6, 'date_create': 0 , 'date_update': 0 }
            tc = EmTestComp.create(**vals)
        with self.assertRaises(TypeError, msg="But invalid keyword argument given"):
            vals = {'invalid': 42, 'name': 'created1', 'rank_fam': 'f', 'string': '{"fr":"testcomp"}', 'help': '{"en":"help test", "fr":"test help"}'}
            tc = EmTestComp.create(**vals)
            
        pass

    def test_create_existing_failure(self):
        """ Testing that create fails when trying to create an EmComponent with an existing name but different properties """
        vals = {'name': 'created1', 'rank_fam': 'f', 'string': '{"fr":"testcomp"}', 'help': '{"en":"help test", "fr":"test help"}'}
        tc = EmTestComp.create(**vals)
        with self.assertRaises(EmComponentExistError, msg="Should raise because attribute differs for a same name"):
            vals['rank_fam'] = 'e'
            EmTestComp.create(**vals)
        pass

    def test_create_existing(self):
        """ Testing that create dont fails when trying to create twice the same EmComponent """
        vals = {'name': 'created1', 'rank_fam': 'f', 'string': '{"fr":"testcomp"}', 'help': '{"en":"help test", "fr":"test help"}'}
        tc = EmTestComp.create(**vals)
        try:
            tc2 = EmTestComp.create(**vals)
        except EmComponentExistError as e:
            self.fail("create raises but should return the existing EmComponent instance instead")
        self.assertEqual(tc.uid, tc2.uid, "Created twice the same EmComponent")
        pass

    def testGetMaxRank(self):
        old = EmTestComp._get_max_rank('f', self.dber)
        EmTestComp.create(name="foobartest", rank_fam = 'f')
        n = EmTestComp._get_max_rank('f', self.dber)
        self.assertEqual(old+1, n, "Excepted value was "+str(old+1)+" but got "+str(n))
        self.assertEqual(EmTestComp._get_max_rank('z', self.dber), -1)
        pass

#====================#
# EmComponent.delete #
#====================#
class TestDelete(ComponentTestCase):
    
    def test_delete(self):
        """ Create and delete TestComponent """
        vals = [
            {'name': 'created1', 'rank_fam': 'f', 'string': '{"fr":"testcomp"}', 'help': '{"en":"help test", "fr":"test help"}'},
            {'name': 'created2', 'rank_fam': 'f', 'string': '{"fr":"testcomp"}', 'help': '{"en":"help test", "fr":"test help"}'},
            {'name': 'created3', 'rank_fam': 'f', 'string': '{"fr":"testcomp"}', 'help': '{"en":"help test", "fr":"test help"}'},
        ]

        tcomps = []

        for val in vals:
            tcomps.append(EmTestComp.create(**val))

        failmsg = "This component should be deleted"

        for i,tcv in enumerate(vals):
            tc = EmTestComp(tcv['name'])
            tc.delete()

            with self.assertRaises(EmComponentNotExistError, msg = failmsg):
                tc2 = EmTestComp(tcv['name'])

            with self.assertRaises(EmComponentNotExistError, msg = failmsg):
                tmp = tc.uid
            with self.assertRaises(EmComponentNotExistError, msg = failmsg):
                tmp = tc.__str__()
            with self.assertRaises(EmComponentNotExistError, msg = failmsg):
                tmp = tc.name
            with self.assertRaises(EmComponentNotExistError, msg = failmsg):
                print(tc)

            for j in range(i+1,len(vals)):
                try:
                    tc = EmTestComp(vals[j]['name'])
                except EmComponentNotExistError:
                    self.fail('EmComponent should not be deleted')
        self.assertTrue(True)
        pass




#===========================#
# EmComponent.modify_rank   #
#===========================#
class TestModifyRank(ComponentTestCase):

    def dump_ranks(self):
        names = [ v['name'] for v in self.test_values ]
        ranks=""
        for i in range(len(names)):
            tc = EmTestComp(names[i])
            ranks += " "+str(tc.rank)
        return ranks

    def test_modify_rank_absolute(self):
        """ Testing modify_rank with absolute rank """
        
        names = [ v['name'] for v in self.test_values ]
        nmax = len(names)-1
        
        #moving first to 3
        #-----------------
        test_comp = EmTestComp(names[0])

        test_comp.modify_rank(3, '=')
        self.assertEqual(test_comp.rank, 3, "Called modify_rank(3, '=') but rank is '"+str(test_comp.rank)+"'. Ranks dump : "+self.dump_ranks())
        tc2 = EmTestComp(names[0])
        self.assertEqual(tc2.rank, 3, "Called modify_rank(3, '=') but rank is '"+str(tc2.rank)+"'. Ranks dump : "+self.dump_ranks())

        for i in range(1,4):
            test_comp = EmTestComp(names[i])
            self.assertEqual(test_comp.rank, i-1, "Excepted rank was '"+str(i-1)+"' but found '"+str(test_comp.rank)+"'. Ranks dump : "+self.dump_ranks())

        for i in [4,nmax]:
            test_comp = EmTestComp(names[i])
            self.assertEqual(test_comp.rank, i, "Rank wasn't excepted to change, but : previous value was '"+str(i)+"' current value is '"+str(test_comp.rank)+"'. Ranks dump : "+self.dump_ranks())

        #undoing last rank change
        test_comp = EmTestComp(names[0])
        test_comp.modify_rank(0,'=')
        self.assertEqual(test_comp.rank, 0)
        tc2 = EmTestComp(names[0])
        self.assertEqual(tc2.rank, 0)

        #moving last to 2
        #----------------
        test_comp = EmTestComp(names[nmax])

        test_comp.modify_rank(2, '=')
        
        for i in [0,1]:
            test_comp = EmTestComp(names[i])
            self.assertEqual(test_comp.rank, i)
        for i in range(3,nmax-1):
            test_comp = EmTestComp(names[i])
            self.assertEqual(test_comp.rank, i+1, "Excepted rank was '"+str(i+1)+"' but found '"+str(test_comp.rank)+"'. Ranks dump : "+self.dump_ranks())

        #undoing last rank change
        test_comp = EmTestComp(names[nmax])
        test_comp.modify_rank(nmax,'=')
        self.assertEqual(test_comp.rank, nmax)
        
        #Checking that we are in original state again
        for i,name in enumerate(names):
            test_comp = EmTestComp(name)
            self.assertEqual(test_comp.rank, i, "Excepted rank was '"+str(i-1)+"' but found '"+str(test_comp.rank)+"'. Ranks dump : "+self.dump_ranks())
        
        #Inverting the list
        #------------------
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
        pass

    def test_modify_rank_relative(self):
        """ Testing modify_rank with relative rank modifier """
        names = [ v['name'] for v in self.test_values ]
        nmax = len(names)-1
        
        test_comp = EmTestComp(names[0])
        #Running modify_rank(i,'+') and the modify_rank(i,'-') for i in range(1,nmax)
        for i in range(1,nmax):
            test_comp.modify_rank(i,'+')
            self.assertEqual(test_comp.rank, i, "The instance (name="+names[0]+") on wich we applied the modify_rank doesn't have expected rank : expected '"+str(i)+"' but got '"+str(test_comp.rank)+"'")
            test_comp2 = EmTestComp(names[0])
            self.assertEqual(test_comp.rank, i, "The instance fetched in Db does'n't have expected rank : expected '"+str(i)+"' but got '"+str(test_comp.rank)+"'")

            for j in range(1,i+1):
                test_comp2 = EmTestComp(names[j])
                self.assertEqual(test_comp2.rank, j-1, self.dump_ranks())
            for j in range(i+1,nmax+1):
                test_comp2 = EmTestComp(names[j])
                self.assertEqual(test_comp2.rank, j, self.dump_ranks())

            test_comp.modify_rank(i,'-')
            self.assertEqual(test_comp.rank, 0, "The instance on wich we applied the modify_rank -"+str(i)+" doesn't have excepted rank : excepted '0' but got '"+str(test_comp.rank)+"'")
            test_comp2 = EmTestComp(names[0])
            self.assertEqual(test_comp.rank, 0, "The instance fetched in Db does'n't have expected rank : expected '0' but got '"+str(test_comp.rank)+"'"+self.dump_ranks())

            for j in range(1,nmax+1):
                test_comp2 = EmTestComp(names[j])
                self.assertEqual(test_comp2.rank, j, self.dump_ranks())

        test_comp = EmTestComp(names[3])
        test_comp.modify_rank(2,'+')
        self.assertEqual(test_comp.rank, 5)
        tc2 = EmTestComp(names[3])
        self.assertEqual(tc2.rank,5)
        for i in [4,5]:
            tc2 = EmTestComp(names[i])
            self.assertEqual(tc2.rank, i-1)
        for i in range(0,3):
            tc2 = EmTestComp(names[i])
            self.assertEqual(tc2.rank, i)

        test_comp.modify_rank(2, '-')
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
            ((-1, '='), ValueError),
            ((-1,), ValueError),
            
            #Bad sign
            ((2, 'a'), ValueError),
            ((1, '=='), ValueError),
            ((1, '+-'), ValueError),
            ((1, 'Hello world !'), ValueError),
            
            #Out of bounds
            ((42*10**9, '+'), ValueError),
            ((-42*10**9, '+'), ValueError),
            ((len(names), '+'), ValueError),
            ((len(names), '-'), ValueError),
            ((len(names), '='), ValueError),
            ((4, '-'), ValueError),
            ((3, '+'), ValueError),
        ]

        for (args, err) in badargs:
            with self.assertRaises(err, msg="Bad arguments supplied : "+str(args)+" for a component at rank 3 but no error raised"):
                tc.modify_rank(*args)
            self.assertEqual(tc.rank, 3, "The function raises an error but modify the rank")
        pass


