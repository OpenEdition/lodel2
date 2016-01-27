## @mainpage
#
# @section Introduction
#
# For basics Lodel2 configuration & usage see README.md
#
# @tableofcontents
#
# @section mainpage_docs Documentation
#
# - Lodel2 architecture : @subpage lodel2_arch 
# - Fieldtypes : @subpage lodel2_fieldtypes
# @subsection mainpage_docs_leapi LeAPI
#
# - LeAPI objects instanciation : @subpage lecrud_instanciation
# - Querying leapi : @subpage api_user_side
#
# @subsection mainpage_docs_configs Lodel2 settings
# - Lodel2 settings handling : @subpage lodel_settings
#
# @section mainpage_pkg_list Main packages
#
# - Lodel
#  - Lodel.settings
# - EditorialModel
#  - EditorialModel.fieldtypes
#  - EditorialModel.backend
# - @ref leapi
# - DataSource
#  - DataSource.MySQL
#

## @page lodel2_arch Lodel2 architecture
#
#
# @section lodel2_arch_basic Lodel2
#
# Lodel 2 is a CMS that allows to define content types ......
#
# @section lodel2_arch_edmod Lodel2 Editorial Model
#
# The editorial model is the part of lodel2 that allows to defines content types.
#
# To handle this the editorial model has 3  abstractions :
# - Classes
# - Types
# - Fields
#
# @warning An editorial model does NOT contains values.
#
# The editorial model is used to generate the dynamic part of the Lodel2 API ( see @ref leapi )
#
# @subsection lodel2_arch_edmod_classes Editorial model classes ( EmClass )
#
# An EmClass is basically a named collection of EmFields ( see @ref lodel2_arch_edmod_fields ) associated with a classtype.
#
# Classtypes are "family" of EmClasses. They defines allowed hierarchical relations between EmClass.
# 
# @subsection lodel2_arch_edmod_types Editorial model types ( EmType )
#
# An EmType is a named EmClass specialization. In fact some EmField in an EmClass can be defined as optionnal and then be selected
# or not to be included in an EmType.
# 
# @subsection lodel2_arch_edmod_fields Editorial model fields ( EmField )
#
# EmFields defines what kind of datas can be stored in EmTypes. Actually its the associationg with an EmFieldtype ( see @ref lodel2_fieldtypes )
# that really defines what kind of datas can be stored.
#
# @subsection lodel2_arch_edmod_fig Editorial model figures
#
# @subsubsection lodel2_arch_edmod_fig_components Editorial model main components
# @image html graphviz/em_components.png
# @subsubsection lodel2_arch_edmod_fig_relations Editorial model relations between components
# @image html graphviz/em_relations.png
# @subsubsection lodel2_arch_edmod_fig_hierarchy Hierarchical relations between EmTypes given a classtype
# @image html graphviz/em_types_hierarch.png
