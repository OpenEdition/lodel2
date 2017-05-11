from flask_script import Command, Option
from management.utils import generate_dyncode

class RefreshDyncode(Command):

    option_list = (
        Option('--model', '-m', dest='model_file'),
        Option('--translator', '-t', dest='translator'),
        Option('--output', '-o', dest='output_filename'),
    )
    
    ## @brief Refreshes the dynamic code in a given output file
    # @param model_file str : file path corresponding to a given editorial model
    # @param translator
    # @param output_filename str : output file for the updated editorial model
    def run(self, model_file, translator, output_filename):
        dyncode = generate_dyncode(model_file, translator)
        with open(output_filename, 'w+') as out_fd:
            out_fd.write(dyncode)
        out_fd.close()
        print("The dynamic code %s has been updated to %s" % (model_file, output_filename)) 

