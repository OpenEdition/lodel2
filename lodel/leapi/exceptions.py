#-*- coding: utf-8 -*-

from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {
    'lodel.exceptions': ['LodelExceptions', 'LodelException']})

##@brief Handles LeApi error
class LeApiError(LodelException):
    pass


##@brief Handles multiple LeAPI errors
class LeApiErrors(LodelExceptions, LeApiError):
    pass


##@brief When an error concerns a data
class LeApiDataCheckError(LeApiError):
    pass

##@brief Handles LeApi data errors
class LeApiDataCheckErrors(LodelExceptions, LeApiError):
    pass


##@brief Handles leapi query errors
class LeApiQueryError(LeApiError):
    pass


##@brief Handles multiple query errors
class LeApiQueryErrors(LodelExceptions, LeApiQueryError):
    pass
