import pkgutil
import os
LODEL_COMMANDS_PATH = os.path.join(__package__, "commands")


def register_commands(manager):
    for _, modulename, _ in pkgutil.iter_modules([LODEL_COMMANDS_PATH]):
        command_module = __import__("%s.%s" % (LODEL_COMMANDS_PATH.replace("/","."),modulename), fromlist=['LodelCommand'])
        manager.add_command(modulename, getattr(command_module, 'LodelCommand')())