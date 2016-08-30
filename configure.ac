AC_INIT([lodel2], [0.1], [contact@openedition.org])

AM_INIT_AUTOMAKE

AC_CONFIG_FILES([Makefile \
	lodel/buildconf.py \
	lodel/Makefile \
	lodel/auth/Makefile \
	lodel/editorial_model/Makefile \
		lodel/editorial_model/translator/Makefile \
	lodel/leapi/Makefile \
		lodel/leapi/datahandlers/Makefile \
	lodel/plugin/Makefile \
	lodel/settings/Makefile \
	lodel/utils/Makefile \
])

m4_include([m4/python.m4])
AM_PATH_PYTHON([3.4.2], [3.5])
PC_INIT([3.4.2], [3.5])
AC_SUBST([PYTHON], [$PYTHON])

PC_PYTHON_CHECK_MODULE([lxml], ,
	AC_MSG_ERROR([Module lxml not found but mandatory for lodel2]))
#Webui deps
AC_SUBST([WEBUI], 'OK')
PC_PYTHON_CHECK_MODULE([jinja2], ,
	AC_MSG_WARN([Module jinja2 not found but mandatory for default web interface])
	AC_SUBST([WEBUI], ''))
PC_PYTHON_CHECK_MODULE([werkzeug], ,
	AC_MSG_WARN([Module werkzeug not found but mandatory for default web interface])
	AC_SUBST([WEBUI], ''))
#Mongo datasource deps
AC_SUBST([MONGODB], 'True')
PC_PYTHON_CHECK_MODULE([pymongo], ,
	AC_MSG_WARN([Module pymongo not found. The mongodb datasource will not be able to work])
	AC_SUBST([MONGODB], 'False'))

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
AC_CHECK_PROGS([DOXYPY], [docypy])
if test -z "$DOXYPY";
then
	AC_MSG_WARN([Doxypy script not found (https://pypi.python.org/pypi/doxypy/0.3) - You will not be able to generate documentation])
	AC_SUBST([DOCOK], '')
fi

AC_OUTPUT

if test -z "$DOCOK";
	then AC_MSG_WARN([You will not be able to generate doxygen documentation. See up for reasons])
fi

if test -z "$WEBUI";
	then AC_MSG_WARN([Mandatory components are missing for running default web UI. See up for reasons])
fi
