#-*- coding: utf-8 -*-
import sys
import os, os.path
sys.path.append(os.path.dirname(os.getcwd()+'/..'))
from lodel.settings.validator import SettingValidator
print(SettingValidator.validators_list_str())
