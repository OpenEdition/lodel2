Common operations :
===================

Configuration file : instance_settings.py

Refresh leapi dynamic code (when the Editorial Model is updated) :
	make refreshdyn

Update or init the database :
	make dbinit

To run an interactive python interpreter in the instance environnment run :
	python loader.py

Instance documentation
======================

loader.py
---------

This file expose all classes needed for a Lodel2 user :
- All the dynamic code classes
- leapidatasource
- migrationhandler

All those classes are imported/exposed given options. LeapiDataSource and the migration handler depends on the choosen datasource, and the dynamic code classes can be wrapped or not by ACL (the acl_bypass configuration variable)

utils.py
--------

This file contains usefull utilities to manage an instance and import & expose the Lodel.settings.Settings class when imported.

THIS FILE HAS TO BE IMPORTED IN ORDER TO BE ABLE TO ACCESS LODEL2 SETTINGS.

### utility functions

- utils.dyn_module_fullname  returns the module fullname for leapi or aclapi (Constant values hardcoded in the loader to be able to use from Foo import * syntax)
- utils.dyn_code_filename : return the python code filename for leapi or aclapi (Constant values)
- utils.refreshdyn : refresh dynamic code
- utils.dbinit : Run full db migration
- utils.em_graph : generate graphviz graph representing the editorial model
- utils.dir_init : ???

instance_settings.py
--------------------

Instance settings file

dyncode directory
-----------------

Contains dynamically generated python code

### dyncode/internal_api.py

leapi dynamically generated code. Import this to be able to use the API without ACL

### dyncode/acl_api.py

ACL wrapper for leapi classes. Public access HAVE TO use the classes defined in this file.

Makefile
--------

Defined target :
- all : refresh dynamic code, init the database and init the directory
- emgraph : generated graphviz graph representing the editorial model
- refreshdyn : refresh dynamic code
- dbinit : init the DB
- dirinit : ???
- clean : clean python *.pyc files and __pycache__ directories
- distclean : call clean target and delete dynamically generated code

em.json
-------

Contains the default EM for an instance

