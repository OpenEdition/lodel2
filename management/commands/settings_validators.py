import sys
import os.path, os.getcwd

from flask_script import Command

from lodel.validator.validator import Validator

class LodelCommand(Command):

    ## @brief Prints the list of the settings validators available in Lodel
    def run(self):
        sys.path.append(os.path.dirname(os.getcwd() + '/..'))
        print(Validator.validators_list_str())

