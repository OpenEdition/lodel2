#-*- coding: utf-8 -*-

import sys
import argparse

try:
    from loader import *
except ImportError: pass

from plugins import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
                        '--list-hooks',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Display the list of registered hooks'
    )
    parser.add_argument(
                        '--list-plugins',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Display the list of plugins'
    )
    parser.add_argument(
                        '--plugin',
                        action='store',
                        type=str,
                        metavar='PLUGIN_NAME',
                        nargs='+',
                        help='Filter on plugins name'
    )
    parser.add_argument(
                        '--hookname',
                        action='store',
                        type=str,
                        metavar='HOOK_NAME',
                        nargs='+',
                        help='Filter on hook name'
    )
    kwargs = parser.parse_args()

    # Listing registered hooks
    if kwargs.list_hooks:
        import Lodel.plugins
        list_args = {}
        if kwargs.plugin is not None and len(kwargs.plugin) > 0:
            list_args['plugins'] = kwargs.plugin
        if kwargs.hookname is not None and len(kwargs.hookname) > 0:
            list_args['names'] = kwargs.hookname
            
        print(Lodel.plugins.list_hooks(**list_args))
        exit(0)
    # Listing plugins
    elif kwargs.list_plugins:
        import Lodel.plugins
        print(Lodel.plugins.list_plugins())
        exit(0)

    parser.print_help()
    exit(1)
