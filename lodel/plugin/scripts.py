import argparse
import sys

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.logger': 'logger',
    'lodel.exceptions': ['LodelException', 'LodelExceptions',
        'LodelFatalError', 'DataNoneValid', 'FieldValidationError']})

## @defgroup lodel2_script Administration scripts
# @ingroup lodel2_plugins

## @package lodel.plugin.scripts Lodel2 utility for writting administration scripts
# @ingroup lodel2_plugins
# @ingroup lodel2_script

## @brief Stores registered scripts
# @todo store it in MetaLodelScript
__registered_scripts = dict()


## @brief LodelScript metaclass that allows to "catch" child class declaration
# @ingroup lodel2_script
# @ingroup lodel2_plugins
#
# Automatic action registration on child class declaration
class MetaLodelScript(type):
    
    ## 
    # @param name str : action's name
    # @param bases list 
    # @param attrs list
    def __init__(self, name, bases, attrs):
        # Here we can store all child classes of LodelScript
        super().__init__(name, bases, attrs)
        if len(bases) == 1 and bases[0] == object:
            return

        self.__register_script(name)
        #_action initialization
        if self._action is None:
            logger.warning("%s._action is None. Trying to use class name as \
action identifier" % name)
            self._action = name
        self._action = self._action.lower()
        if self._description is None:
            self._description = self._default_description()
        self._parser = argparse.ArgumentParser(
            prog = self._prog_name(),
            description = self._description)
        self.argparser_config(self._parser)
            
    
    ## @brief Handles script registration
    # @note Script list is maitained in lodel.plugin.admin_script.__registered_scripts
    # @param name str
    def __register_script(self, name):
        if self._action is None:
            logger.warning("%s._action is None. Trying to use class name as \
action identifier" % name)
            self._action = name
        self._action = self._action.lower()
        script_registration(self._action, self)

    def __str__(self):
        return '%s : %s' % (self._action, self._description)


## @brief Class designed to facilitate custom script writting
# @ingroup lodel2_plugins
# @ingroup lodel2_script
class LodelScript(object, metaclass=MetaLodelScript):
    
    ## @brief A string to identify the action
    _action = None
    ## @brief Script descripiton (argparse argument)
    _description = None
    ## @brief argparse.ArgumentParser instance
    _parser = None
    
    ## @brief No instanciation
    def __init__(self):
        raise NotImplementedError("Static class")
    
    ## @brief Virtual method. Designed to initialize arguement parser.
    # @param parser ArgumentParser : Child class argument parser instance
    # @return MUST return the argument parser (NOT SURE ABOUT THAT !! Maybe it works by reference)
    # @throw LodelScriptError in case it is not implemented in the child class
    @classmethod
    def argparser_config(cls, parser):
        raise LodelScriptError("LodelScript.argparser_config() is a pure \
virtual method! MUST be implemented by ALL child classes")
    
    ## @brief Virtual method. Runs the script
    # @param args list
    # @return None or an integer that will be the script return code
    # @throw LodelScriptError in case it is not implemented in the child class
    @classmethod
    def run(cls, args):
        raise LodelScriptError("LodelScript.run() is a pure virtual method. \
MUST be implemented by ALL child classes")
    
    ## @brief Executes a script
    # 
    # Called by main_run()
    #
    # Handles argument parsing and then call LodelScript.run()
    @classmethod
    def _run(cls):
        args = cls._parser.parse_args()
        return cls.run(args)

    ## @brief Append action name to the prog name
    # @note See argparse.ArgumentParser() prog argument
    # @return str
    @classmethod
    def _prog_name(cls):
        return '%s %s' % (sys.argv[0], cls._action)
    
    ## @brief Return the default description for an action
    # @return str
    @classmethod
    def _default_description(cls):
        return "Lodel2 script : %s" % cls._action
    
    ## @brief handles the help message of an action
    # @param msg str
    # @param return_code int : the default return code is 1
    # @param exit_after bool : default value is True, so that there is an exit after the message printing
    @classmethod
    def help_exit(cls,msg = None, return_code = 1, exit_after = True):
        if not (msg is None):
            print(msg, file=sys.stderr)
        cls._parser.print_help()
        if exit_after:
            exit(1)


## @brief Registers the script class for an action
# @param action_name str
# @param cls LodelScript
def script_registration(action_name, cls):
    __registered_scripts[action_name] = cls
    logger.info("New script registered : %s" % action_name)


## @brief Returns a list containing all available actions
# @return list
def _available_actions():
    return [ act for act in __registered_scripts ]


## @brief Returns default runner's argument parser
# @param ArgumentParser
def _default_parser():

    action_list = _available_actions()
    if len(action_list) > 0:
        action_list = ', '.join(sorted(action_list))
    else:
        action_list = 'NO SCRIPT FOUND !'

    parser = argparse.ArgumentParser(description = "Lodel2 script runner")
    parser.add_argument('-L', '--list-actions', action='store_true',
        default=False, help="List available actions")
    parser.add_argument('action', metavar="ACTION", type=str,
        help="One of the following actions : %s" % action_list, nargs='?')
    parser.add_argument('option', metavar="OPTIONS", type=str, nargs='*',
        help="Action options. Use %s ACTION -h to have help on a specific \
action" % sys.argv[0])
    return parser

## @brief Main function of lodel_admin.py script
#
# This function take care to run the good plugins and clean sys.argv from
# action name before running script
#
# @return DO NOT RETURN BUT exit() ONCE SCRIPT EXECUTED !!
def main_run():
    default_parser = _default_parser()
    if len(sys.argv) == 1:
        default_parser.print_help()
        exit(1)
    #preparing sys.argv (deleting action)
    action = sys.argv[1].lower()
    if action not in __registered_scripts:
        #Trying to parse argument with default parser
        args = default_parser.parse_args()
        if args.list_actions:
            print("Available actions :")
            for sname in sorted(__registered_scripts.keys()):
                print("\t- %s" % __registered_scripts[sname])
            exit(0)

        print("Unknow action '%s'\n" % action, file=sys.stderr)
        default_parser.print_help()
        exit(1)
    #OK action is known, preparing argv to pass it to the action script
    del(sys.argv[1])
    script = __registered_scripts[action]
    ret = script._run()
    ret = 0 if ret is None else ret
    exit(ret)

## @page lodel2_script_doc Lodel2 scripting
# @ingroup lodel2_script
#
# @section lodel2_script_adm Lodel2 instance administration scripts
#
# In Lodel2, it is possible to administrate instances using either Makefiles
# or lodel_admin.py script ( see @ref lodel2_instance_admin ).
#
# The lodel_admin.py script takes an action as first argument. Each action
# corresponds to a sub-script with its own options etc. To get a list
# of all available action run <code>python3 lodel_admin.py -L</code>.
#
# @section lodel2_script_action lodel_admin.py actions
#
# Action implementation is done by class inheritance. To create a new action,
# one has to write a @ref lodel.plugin.scripts.LodelScript "LodelScript" 
# derived class ( see @ref lodel.plugin.core_scripts "core_scripts.py" file 
# as example )
#
# @subsection lodel2_script_inheritance LodelScript inheritance
#
# In order to implement properly a new action you have to write a new 
# @ref lodel.plugin.scripts.LodelScript "LodelScript" derivated class.
# Some methods and attributes are mandatory to write a fully functionnal
# derivated class. Here is a list :
#
# - mandatory methods
#  - @ref plugin.scripts.LodelScript.argparser_config() "argparser_config()" :
#(classmethod) initialize argparse.Parser
#  - @ref plugin.scripts.LodelScript.run() "run()" : (classmethod) contains the
#code that runs to perform the action
# - mandatory attributes
#  - @ref plugin.scripts.LodelScript::_action "_action" : (class attribute)
#stores action name
#  - @ref plugin.scripts.LodelScript::_description "_description" : (class 
#attribute) sotres a short action description
#
# @note On script's action registration : once child class is written you only
# need to import it to trigger script's action registration (see
# @ref plugin.scripts.MetaLodelScript )
#
