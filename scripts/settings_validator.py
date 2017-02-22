#-*- coding: utf-8 -*-
import sys
import os, os.path
sys.path.append(os.path.dirname(os.getcwd()+'/..'))
from lodel.validator.validator import Validator
print(Validator.validators_list_str())
