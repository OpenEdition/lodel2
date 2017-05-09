from flask_script import Command, Option

from management.utils import generate_dyncode

class LodelCommand(Command):

    option_list = (
        Option('--model', '-m', dest='model_file'),
        Option('--translator', '-t', dest='translator'),
    )
    
    ## @brief Generates the dynamic code corresponding to an editorial model
    # @param model_file str : file path corresponding to a given editorial model
    # @param translator
    # @return module
    def run(self, model_file, translator):
        dyncode = generate_dyncode(model_file, translator)        
        print("Dyncode successfully generated for the editorial model from the file %s" % model_file)
        return dyncode
