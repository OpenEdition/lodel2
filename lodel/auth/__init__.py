##@package lodel.auth Package handling authentication on Lodel2
#
#The authentication mechanism are divided in multiple peaces : 
#- The client ( @ref lodel.auth.auth.Client ) singleton class that stores
#clients infos
#- The @ref lodel.auth.Auth class handles authentication, sessions
#creation/load/deletion
#- The session handler implement as a plugin
#
#@par Client class
#
#The @ref lodel.auth.auth.Client class is an abstract singleton. It is designed
#to be implemented by UI plugins. In fact we don't have the same client
#informations on a web UI, on a CLI or with UDP communications. The main goal
#of this class is to provide an API to interface plugins to stores client
#informations allowing lodel2 to produce security log messages containing 
#client informations.
#
#@par Auth class
#
#The auth class is a singleton designed to actually do authentication.
#This class fetch from settings the Emclass and it's field that contains
#login and password. It's also an API between Client class and session handler
#
#@par Session handler
#
#Implemented as a plugin, called with hooks.
