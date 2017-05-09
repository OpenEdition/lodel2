import pkgutil
import os
from lodel.editorial_model.model import EditorialModel
from lodel.leapi import lefactory
LODEL_COMMANDS_PATH = os.path.join(__package__, "commands")


def register_commands(manager):
    for _, modulename, _ in pkgutil.iter_modules([LODEL_COMMANDS_PATH]):
        command_module = __import__("%s.%s" % (LODEL_COMMANDS_PATH.replace("/","."),modulename), fromlist=['LodelCommand'])
        manager.add_command(modulename, getattr(command_module, 'LodelCommand')())

##
# @todo move this method in the corresponding module and change its calls in the corresponding commands
def generate_dyncode(model_file, translator):
    model = EditorialModel.load(translator, filename=model_file)
    dyncode = lefactory.dyncode_from_em(model)
    return dyncode
