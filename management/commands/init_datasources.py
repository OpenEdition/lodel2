from flask_script import Command, Option

from management.utils import init_all_datasources

class InitDataSources(Command):

    option_list = (
        Option('--dyncode', '-m', dest='dyncode'),
    )
    
    ## @brief Generates the dynamic code corresponding to an editorial model
    # @param model_file str : file path corresponding to a given editorial model
    # @param translator
    # @return module
    def run(self, dyncode):
        init_all_datasources(dyncode)       
        print("Datasources successfully started")
