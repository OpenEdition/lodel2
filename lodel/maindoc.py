#-*- coding: utf-8 -*-

## @mainpage
#
# @section lodel_general_description General Description
# Lodel is a web publishing system which is configurable to one's specific needs. It is a member of the content management systems' category.
#
# In its 2.0 version, it is composed from a main package, called "lodel" which contains all of its core packages and modules.
#
# @section lodel_core_components Core Components
# The application contains the following packages in its core :
#
# - lodel.auth : the authentication system used to deal with the users' sessions
# - lodel.editorial_model : a package containing all the tools to read/write/update an editorial model
# - lodel.leapi : the main API that will be used to access the documents' data
# - lodel.plugin : a plugin manager (with modules to deal with the hooks, the scripts, the options, etc ... brought in by each plugin)
# - lodel.plugins : this package is used to store all the plugins that are added in Lodel
# - lodel.settings : the settings management tools
# - lodel.utils : several small tools that are useful and common to several core modules
#
# Aside from that, there are core modules :
# - lodel.context : the context manager (used for the multisite functionality)
# - lodel.logger : a global logging tool
#
# @section one_code_and_multiple_websites One code and multiple websites
# Lodel can be used to manage one or many websites using the same core code. Each website will have its own activated plugins,
# editorial model options and settings, all managed by the context manager.
#