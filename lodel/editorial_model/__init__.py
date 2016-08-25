##@defgroup lodel2_em Editorial Model
#@brief Data organisation description

##@package lodel.editorial_model
#@brief Editorial model package
#
#The editorial model defines objects with fields. This objects will be later
#manipulated via @ref lodel.leapi "LeAPI"

##@page lodel2_em_page Editorial Model
#@ingroup lodel2_em
#
#@section lodel2_em_what What is an editorial model ?
#
#The editorial model is a kind of entity-relationship model describing
#editorial objects.
#
#@warning The lodel.editorial_model package does not contains code executed by
#instances. The editorial model is used to generate python code named 
#@ref lodel2_leapi "LeAPI" and the package contains Classes that made easy
#the Em manipulation
#
# @subsection lodel2_em_class EmClass
#
#An editorial object is named @ref components.EmClass "EmClass" for "Editorial
# Model Class". A class is characterized by a uniq name a 
#@ref lodel2_datasources "Datasource", a group, an optionnal parent EmClass and
#the @ref components.EmField "EmFields" it contains.
#
#@par Example
#<code>An "Article" is an EmClass with "article" as name, the EmClass "Text" as
#parent etc...</code>
#
# @subsection lodel2_em_field EmField
#
#@ref components.EmClass "EmClasses" contains 
#@ref components.EmField "EmFields". An EmField as a name (uniq in the EmClass)
# and is associated to a @ref lodel2_datahandlers "DataHandler" specification.
#
# @subsection lodel2_em_group EmGroup
#
#@ref components.EmClass "EmClasses" and @ref components.EmField "EmFields"
#are in @ref components.EmGroup "EmGroups". EmGroups represent a consistent
#EditorialModel part that can be activated or deactivated.
#
#@par Example
#<pre>EmGroup "authors" contains the EmClass authors and all its EmField
# + "written_by" EmField (a reference field on "Author" EmClass) in the EmClass
#"Text"</pre>
#
