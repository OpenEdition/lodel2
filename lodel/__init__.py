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
