from lodel.leapi.datahandlers.base_classes import DataHandler
DataHandler.load_base_handlers()

##@defgroup lodel2_datahandlers Datahandlers
#@ingroup lodel2_leapi
#@ingroup lodel2_em

##@defgroup lodel2_dh_checks  Datahandlers datas checking
#@ingroup lodel2_datahandlers

##@package lodel.leapi.datahandlers Lodel2 datahandlers
#
#Datahandlers are object that handles datas check, construction and 
#consistency check
#


##@page lodel2_dh_checks_page Datahandlers datas checking
#@ingroup lodel2_dh_checks
#
#@section lodel2_dh_check_mech Datas checking mechanism
#
#The data checking mechanism is divided into 3 stages :
# 1. **value checking** : a basic value check. Example : is len(value) < 52
# 2. **data construction** : for datas that needs to be modified. Example :
#a date that will be transformed into a Datetime object associated with
#a timezone
# 3. **data consistency checking** : perform a consistency checking on the 
#object from the "point of view" of the current field. Example : is the given
#lodel_id an identifier of a Article
#
#@subsection lodel2_dh_check_impl Implementation
#
#Those three stages are implemented by 3 datahandlers methods :
# - @ref base_classes.DataHandler.check_data_value() "check_data_value"
# - @ref base_classes.DataHandler.construct_data() "construct_data"
# - @ref base_classes.DataHandler.check_data_value() "check_data_consitency"
#
#@note To ensure the calls of the base classes methods child classes implements
#those method with a '_' preffix : 
# - @ref base_classes.DataHandler._check_data_value "_check_data_value()"
# - @ref base_classes.DataHandler._construct_data() "_construct_data"
# - @ref base_classes.DataHandler._check_data_value() "_check_data_consitency"
#
#Examples of child classes can be found @ref datahandlers.datas "here"
#
#@subsubsection lodel2_dh_datas_construction Datas construction
#
#Datas construction is a bit tricky. When constructing a data handled by a
#datahandler we may need to have access to other datas in the object (see 
#@ref base_classes.DataHandler.construct_data() "construct_data() arguments").
#
#The problem reside in the construction order, if we need other datas we have
#to be sure that they are allready constructed. To achieve this goal the datas
#dict given as arguement to 
#@ref base_classes.DataHandler.construct_data() "construct_data()" is an
#@ref base_classes.DatasConstructor "DatasConstructor" instance. This class
#check if a data is constructed when trying to access to it, if not it runs
#the corresponding construct_data() (and have a circular dependencies detection
#mechanism)
#
#@see base_classes.DatasConstructor.
