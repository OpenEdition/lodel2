#-*- coding: utf-8 -*-
## @package Lodel.settings_format Rules for settings

## @brief List mandatory configurations keys
MANDATORY = [
    'debug',
    'debug_sql',
    'sitename',
    'lodel2_lib_path',
    'em_file',
    'dynamic_code_file',
    'acl_dyn_api',
    'ds_package',
    'datasource',
    'mh_classname',
    'migration_options',
    'base_path'
]

## @brief List allowed (but not mandatory) configurations keys
ALLOWED = [
    'em_graph_output',
    'em_graph_format',
    'templates_base_dir'
]
