AC_INIT([lodel], [0.1], [contact@openedition.org])

AM_INIT_AUTOMAKE

AC_CONFIG_FILES([Makefile \
	lodel/buildconf.py.am \
	lodel/Makefile \
	lodel/auth/Makefile \
	lodel/editorial_model/Makefile \
		lodel/editorial_model/translator/Makefile \
	lodel/leapi/Makefile \
		lodel/leapi/datahandlers/Makefile \
	lodel/plugin/Makefile \
	lodel/settings/Makefile \
	lodel/validator/Makefile \
	lodel/mlnamedobject/Makefile \
	lodel/utils/Makefile \
	progs/Makefile \
	progs/slim/Makefile \
	lodel/plugins/Makefile
])


###
#Kind of dangerous mix between default aclocal's macro and pyconfigure macros...
#
#pyconfigure macros are prefixed by PC_
###
AC_PROG_LN_S
AC_PROG_MKDIR_P

m4_include([m4/python.m4]) # Patched version of aclocal python.m4 file
m4_include([m4/python_pyconfigure.m4]) #Renamed because we use a patched version of aclocal python.m4 file
m4_define(python_min_ver, 3.4.2)

AM_PATH_PYTHON([3.4.2]) #init aclocal's default python support
PC_INIT([3.4.2], [3.5]) #init pyconfigure aclocal's macro

PC_PYTHON_VERIFY_VERSION([>=], python_min_ver, ,
	[AC_MSG_ERROR(Python interpreter too old)])

AC_ARG_VAR([SITEPACKAGES], [If installed in /usr or /System* specify the name of the site directory (default value "site-packages"])

PC_PYTHON_CHECK_MODULE([lxml], ,
	AC_MSG_ERROR([Module lxml not found but mandatory for lodel2]))
#Webui deps
AC_SUBST([WEBUI], 'True')
PC_PYTHON_CHECK_MODULE_VERSION([jinja2], [2.7.3], [], ,
	AC_MSG_WARN([Module jinja2 not found but mandatory for default web interface])
	AC_SUBST([WEBUI], 'False'))
PC_PYTHON_CHECK_MODULE_VERSION([werkzeug], [0.9], [], , 
	AC_MSG_WARN([Module werkzeug not found but mandatory for default web interface])
	AC_SUBST([WEBUI], 'False'))
#Mongo datasource deps
AC_SUBST([PYMONGO], 'True') #Can be found in lodel/buildconf.py
PC_PYTHON_CHECK_MODULE_VERSION([pymongo], [2.7], [2.8], ,
	AC_MSG_WARN([Module pymongo not found. The mongodb datasource will not be able to work])
	AC_SUBST([PYMONGO], 'False')
)


#Documentation checks
AC_SUBST([DOCOK], 'OK')
AC_CHECK_PROGS([DOXYGEN], [doxygen])
if test -z "$DOXYGEN";
then
	AC_MSG_WARN([Doxygen not found - You will not be able to generate documentation])
	AC_SUBST([DOCOK], '')
fi
AC_CHECK_PROGS([GRAPHVIZ], [dot neato twopi])
if test -z "$GRAPHVIZ";
then
	AC_MSG_WARN([Graphviz not found (dot executable missing) - You will not be able to generate documentation])
	AC_SUBST([DOCOK], '')
fi
AC_CHECK_PROGS([DOXYPY], [doxypy])
if test -z "$DOXYPY";
then
	AC_MSG_WARN([Doxypy script not found (https://pypi.python.org/pypi/doxypy/0.3) - You will not be able to generate documentation])
	AC_SUBST([DOCOK], '')
fi

AC_OUTPUT

if test -z "$DOCOK";
	then AC_MSG_WARN([You will not be able to generate doxygen documentation. See up for reasons])
fi

if test "$WEBUI" = 'False';
	then AC_MSG_WARN([Mandatory components are missing for running default web UI. See up for reasons])
fi

if test "$PYMONGO" = 'False';
	then AC_MSG_WARN([You will not be able to user mongodb datasource. See up for reasons])
fi
