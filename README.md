- use python 3.4

** install dependencies
  pip install -r requirements.txt

------

Creating a Lodel "instance":

use the lodel_init.sh script :
	lodel_init.sh INSTANCE_NAME INSTANCE_WANTED_PATH [LODEL2_LIB_PATH]
	cd INSTANCE_PATH

Create a database for your instance
  mysql
  > CREATE DATABASE `lodel2`  CHARACTER SET utf8 COLLATE utf8_general_ci;
  > GRANT ALL ON `lodel2`.* TO "lodel"@"localhost";

Edit instance_settings.py according to your database, install database and dynamic code
	make

Once the instance is created you can run an interactive python interpreter using :
	python loader.py

If you want to write a script that run is the instance env you have to use
	from loader import *

-----

Lodel2 plugins system:

In an instance or in the lib dir you can ask Lodel2 wich plugins and wich hooks are activated.
Print a list of plugins :
	python3 manage_lodel.py --list-plugins
Print a list of registered hooks :
	python3 manage_lodel.py --list-hooks
More informations about the script :
	python3 manage_lodel.py --help

-----

** Doxygen generation
  Dependencies : doxygen graphviz doxypy
  Generation : run make doc in the root folder

** create local config in settings.py
Copy settings.py.example to settings.py, change the conf to your local settings

** Tools

  A Makefile is written with common operations :
  - make clean : cleans doc and python pycache (and .pyc files)
  - make pip : upgrade python libs according to requirements.txt
  - make doc : generate the doxygen documentation
  - make check : run the unit tests
  - make : run check doc and pip
