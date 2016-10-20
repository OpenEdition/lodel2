##@brief Designed to be the base class for all exceptions of this module
class MultiSiteError(Exception):
    pass

##@brief Designed to be thrown on site identifier errors
class MultiSiteIdentifierError(MultiSiteError):
    pass

