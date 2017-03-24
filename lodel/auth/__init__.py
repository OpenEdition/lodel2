##@package lodel.auth Package handling authentication on Lodel2
#
#The authentication mechanism is divided in multiple pieces :
#- The client ( @ref lodel.auth.auth.Client ) singleton class that stores
# and uses the clients' informations
#- The session handler, implemented as a plugin
#
#@par Client class
#
#The @ref lodel.auth.auth.Client class is an abstract singleton. It is designed
#to be implemented by UI plugins. In fact we don't have the same client
#informations on a web UI, on a CLI or with UDP communications. The main goal
#of this class is then to provide an API to interface plugins to stores client
#informations allowing lodel2 to produce security log messages containing 
#client informations.
#
#@par Session handler
#
# The session handler is implemented as a plugin, called by hooks.
