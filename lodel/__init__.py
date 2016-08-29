#-*- coding: utf-8 -*-

dyncode = None

##@page lodel2_start Lodel2 boot mechanism
#
# @par Lodel2 boot sequence
# see @ref install/loader.py
# 1. lodel package is imported
# 2. settings are started 
# 3. plugins are pre-loaded from conf to load plugins configuration specs
# 4. settings are loaded from conf and checked
# 3. plugins are loaded (hooks are registered etc)
# 4. "lodel2_bootstraped" hooks are called
# 5. "lodel2_loader_main" hooks are called (if runned from loader.py as main executable)
#

##@page lodel2_instance_admin Lodel2 instance administration
#
#@section lodel2_instance_adm_tools Tools
#
#@subsection lodel2_instance_makefile Makefile
#
#The Makefile allows to run automated without arguments such as :
#- refresh the dynamic code using conf + EM (target **dyncode**)
#- update databases (target **init_db**)
#- refresh plugins list (target **refresh_plugins**)
#
#@subsection lodel2_instance_adm_scripts lodel_admin.py scripts
#
#In all instances you find a symlink named lodel_admin.py . This script
#contains the code run by @ref lodel2_instance_makefile "Makefile targets"
#and a main function that allows to run it as a CLI script.
#
#@par Script help
#<pre>
#usage: lodel_admin.py [-h] [-L] [ACTION] [OPTIONS [OPTIONS ...]]
#
#Lodel2 script runner
#
#positional arguments:
#  ACTION              One of the following actions : discover-plugin [...]
#  OPTIONS             Action options. Use lodel_admin.py ACTION -h to have
#                      help on a specific action
#
#optional arguments:
#  -h, --help          show this help message and exit
#  -L, --list-actions  List available actions
#</pre>
#
#@par Script customization
#
#See @ref lodel2_script_doc "Lodel2 scripting"
#
#

