## @package plugins Lodel2 plugin system
#
# The plugins activation system is based on <code>__init__.py</code> file.
# The <code>__all__</code> variable in @ref plugins/__init__.py is generated
# from configuration by Lodel.plugins._all_plugins() method. Then the plugins should
# auto-import all its source files using it's own package <code>__init__.py</code> file
#
# For the moment plugins capabilities are :
# - Hooks registration using Lodel.LodelHook decoration class
# - User authentification methods registration using Lodel.user.authentication_method decorator
# - User identification methods using Lodel.user.identification_method decorator
#
# You can find examples plugins in :
# - plugins.dummy (Hooks registration)
# - plugins.dummy_auth (Auth and identification methods registration)
# - plugins.dummy_acl (Complex plugin with settings enhancement example)
#
import Lodel.plugins
## @brief Contain all activated plugins name
__all__ = Lodel.plugins._all_plugins()
