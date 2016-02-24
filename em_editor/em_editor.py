#-*- coding: utf-8 -*-
from loader import *

import os, os.path, code

from EditorialModel.model import Model
from EditorialModel.backend.json_backend import EmBackendJson
from EditorialModel.classes import EmClass
from EditorialModel.types import EmType
from EditorialModel.fields import EmField
from EditorialModel.classtypes import *

emfile = input("Enter em path please : ")

if not os.path.isfile(emfile):
    with open(emfile,'w+') as fd:
        fd.write('{}')

em = Model(EmBackendJson(emfile))

print("Editorial model loaded in em variable : ")
for comptype in [ 'EmClass', 'EmType', 'EmField' ]:
    print("\t* %s :" % comptype)
    complist = em.components(comptype)
    if len(complist) == 0:
        print("\t\tEMPTY")
    for comp in complist:
       print("\t\t- %s" % comp.name)


code.interact(local=locals())

