#!/usr/bin/env python3
#-*- coding: utf-8 -*-


INSTANCES_ABSPATH="/tmp/lodel2_instances"
STORE_FILE='./instances.json'
CREATION_SCRIPT='../scripts/create_instance.sh'
INSTALL_TPL = './slim_ressources/slim_install_model'
EMFILE = './slim_ressources/emfile.pickle'

import os, os.path
import sys
import shutil
import argparse
import logging
import json

logging.basicConfig(level=logging.INFO)

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
    store_datas = get_store_datas()
    logging.warning("Deleting instance %s" % name)
    logging.info("Deleting instance folder %s" % store_datas[name]['path'])
    shutil.rmtree(store_datas[name]['path'])
    logging.info("Deleting instance from json store file")
    del(store_datas[name])
    save_datas(store_datas)

##@brief returns stored datas
def get_store_datas():
    if not os.path.isfile(STORE_FILE):
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

##@brief Print the list of instances and exit
def list_instances(verbosity):
    if not os.path.isfile(STORE_FILE):
        print("No store file, no instances are existing. Exiting...",
            file=sys.stderr)
        exit(0)
    print('Instances list :')
    exit(0)

##@brief Returns instanciated parser
def get_parser():
    parser = argparse.ArgumentParser(
        description='SLIM (Simple Lodel Instance Manager.)')
    selector = parser.add_argument_group('Instances selectors')
    actions = parser.add_argument_group('Instances actions')
    parser.add_argument('-l', '--list', 
        help='list existing instances and exit', action='store_const',
        const=True, default=False)
    parser.add_argument('-v', '--verbose', action='count')
    actions.add_argument('-c', '--create', action='store_const',
        default=False, const=True,
        help="Create a new instance with given name (see -n --name)")
    actions.add_argument('-d', '--delete', action='store_const',
        default=False, const=True,
        help="Delete an instance with given name (see -n --name)")
    actions.add_argument('-e', '--edit-config', action='store_const',
        default=False, const=True,
        help='Edit configuration of specified instance')
    selector.add_argument('-a', '--all', action='store_const',
        default=False, const=True,
        help='Select all instances')
    selector.add_argument('-n', '--name', metavar='NAME', type=str, nargs='*',
        help="Specify an instance name")
    actions.add_argument('--stop', action='store_const', 
        default=False, const=True, help="Stop instances")
    actions.add_argument('--start', action='store_const', 
        default=False, const=True, help="Start instances")
    actions.add_argument('-m', '--make', metavar='TARGET', type=str,
        nargs="?", default='not',
        help='Run make for selected instances')
    return parser

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    if args.list:
        list_instances(args.verbose)
    elif args.create:
        if args.name is None:
            parser.print_help()
            print("\nAn instance name expected when creating an instance !",
                file=sys.stderr)
            exit(1)
        for name in args.name:
            new_instance(name)
    elif args.delete:
        if args.name is None:
            parser.print_help()
            print("\nAn instance name expected when creating an instance !",
                file=sys.stderr)
            exit(1)
        validate_names(args.name)
        for name in args.name:
            delete_instance(name)
    elif args.make != 'not':
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
        names = get_specified(args)
        if len(names) > 1:
            print("\n-e --edit-config option works only when 1 instance is \
specified")
        validate_names(names)
        name = names[0]
        store_datas = get_store_datas()
        conffile = os.path.join(store_datas[name]['path'], 'conf.d')
        conffile = os.path.join(conffile, 'lodel2.ini')
        os.system('editor "%s"' % conffile)
        exit(0)
