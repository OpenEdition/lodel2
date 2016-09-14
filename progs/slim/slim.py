#!/usr/bin/env python3
#-*- coding: utf-8 -*-


import os, os.path
import sys
import shutil
import argparse
import logging
import re
import json
import configparser
import subprocess

logging.basicConfig(level=logging.INFO)

INSTANCES_ABSPATH="/tmp/lodel2_instances"
CONFFILE='conf.d/lodel2.ini'
try:
    STORE_FILE = os.path.join("[@]SLIM_VAR_DIR[@]", 'slim_instances.json')
    PID_FILE = os.path.join("[@]SLIM_VAR_DIR[@]", 'slim_instances_pid.json')
    CREATION_SCRIPT = os.path.join("[@]LODEL2_PROGSDIR[@]", 'create_instance')
    INSTALL_TPL = "[@]SLIM_INSTALLMODEL_DIR[@]"
    EMFILE = os.path.join("[@]SLIM_DATADIR[@]", 'emfile.pickle')

except SyntaxError:
    STORE_FILE='./instances.json'
    PID_FILE = './slim_instances_pid.json'
    CREATION_SCRIPT='../scripts/create_instance.sh'
    INSTALL_TPL = './slim_ressources/slim_install_model'
    EMFILE = './slim_ressources/emfile.pickle'



    CREATION_SCRIPT=os.path.join(os.path.dirname(__file__), CREATION_SCRIPT)
    STORE_FILE=os.path.join(os.path.dirname(__file__), STORE_FILE)
    INSTALL_TPL=os.path.join(os.path.dirname(__file__), INSTALL_TPL)
    EMFILE=os.path.join(os.path.dirname(__file__), EMFILE)


#STORE_FILE syntax :
#
#First level keys are instances names, their values are dict with following
#informations : 
# - path
#

##@brief Run 'make %target%' for each instances given in names
#@param target str : make target
#@param names list : list of instance name
def run_make(target, names):
    validate_names(names)
    store_datas = get_store_datas()
    cwd = os.getcwd()
    for name in [n for n in store_datas if n in names]:
        datas = store_datas[name]
        logging.info("Running 'make %s' for '%s' in %s" % (
            target, name, datas['path']))
        os.chdir(datas['path'])
        os.system('make %s' % target)
    os.chdir(cwd)
            

##@brief Set configuration given args
#@param args as returned by argparse
def set_conf(name, args):
    validate_names([name])
    conffile = get_conffile(name)
    

    config = configparser.ConfigParser(interpolation=None)
    config.read(conffile)


    if args.interface is not None:
        if args.interface not in ('web', 'python'):
            raise TypeError("Interface can only be on of : 'web', 'python'")
        config['lodel2']['interface'] = args.interface
    interface = config['lodel2']['interface']
    if interface == 'web':
        if 'lodel.webui' not in config:
            config['lodel.webui'] = dict()
            config['lodel.webui']['standalone'] = 'True'
        if args.listen_port is not None:
            config['lodel.webui']['listen_port'] = str(args.listen_port)
        if args.listen_address is not None:
            config['lodel.webui']['listen_address'] = str(args.listen_address)
    else: #interface is python
        if args.listen_port is not None or args.listen_address is not None:
            logging.error("Listen port and listen address will not being set. \
Selected interface is not the web iterface")
        if 'lodel.webui' in config:
            del(config['lodel.webui'])
    #Now config should be OK to be written again in conffile
    with open(conffile, 'w+') as cfp:
        config.write(cfp)

##@brief If the name is not valid raise
def name_is_valid(name):
    allowed_chars = [chr(i) for i in range(ord('a'), ord('z')+1)]
    allowed_chars += [chr(i) for i in range(ord('A'), ord('Z')+1)]
    allowed_chars += [chr(i) for i in range(ord('0'), ord('9')+1)]
    allowed_chars += ['_']
    for c in name:
        if c not in allowed_chars:
            raise RuntimeError("Allowed characters for instance name are \
lower&upper alphanum and '_'. Name '%s' is invalid" % name)

##@brief Create a new instance
#@param name str : the instance name
def new_instance(name):
    name_is_valid(name)
    store_datas = get_store_datas()
    if name in store_datas:
        logging.error("An instance named '%s' already exists" % name)
        exit(1)
    if not os.path.isdir(INSTANCES_ABSPATH):
        logging.info("Instances directory '%s' don't exists, creating it")
        os.mkdir(INSTANCES_ABSPATH)
    instance_path = os.path.join(INSTANCES_ABSPATH, name)
    creation_cmd = '{script} "{name}" "{path}" "{install_tpl}" \
"{emfile}"'.format(
        script = CREATION_SCRIPT,
        name = name,
        path = instance_path,
        install_tpl = INSTALL_TPL,
        emfile = EMFILE)
    res = os.system(creation_cmd)
    if res != 0:
        logging.error("Creation script fails")
        exit(res)
    #storing new instance
    store_datas[name] = {'path': instance_path}
    save_datas(store_datas)

##@brief Delete an instance
#@param name str : the instance name
def delete_instance(name):
    if get_pid(name) is not None:
        logging.error("The instance '%s' is started. Stop it before deleting \
it" % name)
    store_datas = get_store_datas()
    logging.warning("Deleting instance %s" % name)
    logging.info("Deleting instance folder %s" % store_datas[name]['path'])
    shutil.rmtree(store_datas[name]['path'])
    logging.info("Deleting instance from json store file")
    del(store_datas[name])
    save_datas(store_datas)

##@brief returns stored datas
def get_store_datas():
    if not os.path.isfile(STORE_FILE) or os.stat(STORE_FILE).st_size == 0:
        return dict()
    else:
        with open(STORE_FILE, 'r') as sfp:
            datas = json.load(sfp)
    return datas

##@brief Checks names validity and exit if fails
def validate_names(names):
    store_datas = get_store_datas()
    invalid = [ n for n in names if n not in store_datas]
    if len(invalid) > 0:
        print("Following names are not existing instance :", file=sys.stderr)
        for name in invalid:
            print("\t%s" % name, file=sys.stderr)
        exit(1)

##@brief Returns the PID dict
#@return a dict with instance name as key an PID as value
def get_pids():
    if not os.path.isfile(PID_FILE):
        return dict()
    with open(PID_FILE, 'r') as pdf:
        return json.load(pfd)

##@brief Save a dict of pid
#@param pid_dict dict : key is instance name values are pid
def save_pids(pid_dict):
    with open(PID_FILE, 'w+') as pfd:
        json.dump(pid_dict, pfd)

##@brief Given an instance name returns its PID
#@return False or an int
def get_pid(name):
    pid_datas = get_pids()
    if name not in pid_datas:
        return False
    else:
        return pid_datas[name]

##@brief Start an instance
#@param names list : instance name list
def start_instance(names):
    pids = get_pids()
    store_datas = get_store_datas()
    
    for name in names:
        if name in pids:
            logging.warning("The instance %s is allready running" % name)
            continue
        os.chdir(store_datas[name]['path'])
        args = [sys.executable, 'loader.py']
        curexec = subprocess.Popen(args)
        pids[name] = curexec.pid
        logging.info("Instance '%s' started. PID %d" % (name, curexec.pid))

##@brief Check if instance are specified
def get_specified(args):
    if args.all:
        names = list(get_store_datas().keys())
    elif args.name is not None:
        names = args.name
    else:
        names = None
    return names

##@brief Saves store datas
def save_datas(datas):
    with open(STORE_FILE, 'w+') as sfp:
        json.dump(datas, sfp)

##@return conffile path
def get_conffile(name):
    validate_names([name])
    store_datas = get_store_datas()
    return os.path.join(store_datas[name]['path'], CONFFILE)

##@brief Print the list of instances and exit
#@param verbosity int
#@param batch bool : if true make simple output
def list_instances(verbosity, batch):
    verbosity = 0 if verbosity is None else verbosity
    if not os.path.isfile(STORE_FILE):
        print("No store file, no instances are existing. Exiting...",
            file=sys.stderr)
        exit(0)
    store_datas = get_store_datas()
    if not batch:
        print('Instances list :')
    for name in store_datas:
        details_instance(name, verbosity, batch)
    exit(0)

##@brief Print instance informations and return (None)
#@param name str : instance name
#@param verbosity int
#@param batch bool : if true make simple output
def details_instance(name, verbosity, batch):
    validate_names([name])
    store_datas = get_store_datas()
    if not batch:
        msg = "\t- '%s'" % name
        if verbosity > 0:
            msg += ' path = "%s"' % store_datas[name]['path']
        if verbosity > 1:
            ruler = (''.join(['=' for _ in range(20)])) + "\n"
            msg += "\n\t\t====conf.d/lodel2.ini====\n"
            with open(get_conffile(name)) as cfp:
                for line in cfp:
                    msg += "\t\t"+line
            msg += "\t\t=========================\n"

        print(msg)
    else:
        msg = name
        if verbosity > 0:
            msg += "\t"+'"%s"' % store_datas[name]['path']
        if verbosity > 1:
            conffile = get_conffile(name)
            msg += "\n\t#####"+conffile+"#####\n"
            with open(conffile, 'r') as cfp:
                for line in cfp:
                    msg += "\t"+line
            msg += "\n\t###########"
        print(msg)
    
##@brief Returns instanciated parser
def get_parser():
    parser = argparse.ArgumentParser(
        description='SLIM (Simple Lodel Instance Manager.)')
    selector = parser.add_argument_group('Instances selectors')
    actions = parser.add_argument_group('Instances actions')
    confs = parser.add_argument_group('Options (use with -c or -s)')

    parser.add_argument('-l', '--list', 
        help='list existing instances and exit', action='store_const',
        const=True, default=False)
    parser.add_argument('-v', '--verbose', action='count')
    parser.add_argument('-b', '--batch', action='store_const',
        default=False, const=True,
        help="Format output (when possible) making it usable by POSIX scripts \
(only implemented for -l for the moment)")
    selector.add_argument('-a', '--all', action='store_const',
        default=False, const=True,
        help='Select all instances')
    selector.add_argument('-n', '--name', metavar='NAME', type=str, nargs='*',
        help="Specify an instance name")

    actions.add_argument('-c', '--create', action='store_const',
        default=False, const=True,
        help="Create a new instance with given name (see -n --name)")
    actions.add_argument('-d', '--delete', action='store_const',
        default=False, const=True,
        help="Delete an instance with given name (see -n --name)")
    actions.add_argument('-s', '--set-option', action='store_const',
        default=False, const=True,
        help="Use this flag to set options on instance")
    actions.add_argument('-e', '--edit-config', action='store_const',
        default=False, const=True,
        help='Edit configuration of specified instance')
    actions.add_argument('-i', '--interactive', action='store_const',
        default=False, const=True,
        help='Run a loader.py from ONE instance in foreground')
    actions.add_argument('--stop', action='store_const', 
        default=False, const=True, help="Stop instances")
    actions.add_argument('--start', action='store_const', 
        default=False, const=True, help="Start instances")
    actions.add_argument('-m', '--make', metavar='TARGET', type=str,
        nargs="?", default='not',
        help='Run make for selected instances')

    confs.add_argument('--interface', type=str,
        help="Select wich interface to run. Possible values are \
'python' and 'web'")
    confs.add_argument('--listen-port', type=int,
        help="Select the port on wich the web interface will listen to")
    confs.add_argument('--listen-address', type=str,
        help="Select the address on wich the web interface will bind to")
    return parser

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    if args.list:
        # Instances list
        if args.name is not None:
            validate_names(args.name)
            for name in args.name:
                details_instance(name, args.verbose, args.batch)
        else:
            list_instances(args.verbose, args.batch)
    elif args.create:
        #Instance creation
        if args.name is None:
            parser.print_help()
            print("\nAn instance name expected when creating an instance !",
                file=sys.stderr)
            exit(1)
        for name in args.name:
            new_instance(name)
    elif args.delete:
        #Instance deletion
        if args.name is None:
            parser.print_help()
            print("\nAn instance name expected when creating an instance !",
                file=sys.stderr)
            exit(1)
        validate_names(args.name)
        for name in args.name:
            delete_instance(name)
    elif args.make != 'not':
        #Running make in instances
        if args.make is None:
            target = 'all'
        else:
            target = args.make
        names = get_specified(args)
        if names is None:
            parser.print_help()
            print("\nWhen using -m --make options you have to select \
instances, either by name using -n or all using -a")
            exit(1)
        run_make(target, names)
    elif args.edit_config:
        #Edit configuration
        names = get_specified(args)
        if len(names) > 1:
            print("\n-e --edit-config option works only when 1 instance is \
specified")
        validate_names(names)
        name = names[0]
        store_datas = get_store_datas()
        conffile = get_conffile(name)
        os.system('editor "%s"' % conffile)
        exit(0)
    elif args.interactive:
        #Run loader.py in foreground
        if args.name is None or len(args.name) != 1:
            print("\n-i option only allowed with ONE instance name")
            parser.print_help()
            exit(1)
        validate_names(args.name)
        name = args.name[0]
        store_datas = get_store_datas()
        os.chdir(store_datas[name]['path'])
        os.execl('/usr/bin/env', '/usr/bin/env', 'python3', 'loader.py')
    elif args.set_option:
        names = None
        if args.all:
            names = list(get_store_datas().values())
        elif args.name is not None:
            names = args.name
        if names is None:
            print("\n-s option only allowed with instance specified (by name \
or with -a)")
            parser.print_help()
            exit(1)
        for name in names:
            set_conf(name, args)
    elif args.start:
        names = get_specified(args)
        start_instance(names)
        
