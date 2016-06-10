#-*- coding: utf-8 -*-

from lodel.exceptions import LodelExceptions, LodelException

class LeApiError(LodelException):
    pass


##@brief Handles multiple LeAPI errors
class LeApiErrors(LodelExceptions, LeApiError):
    pass


##@brief When an error concerns a datas
class LeApiDataCheckError(LeApiError):
    pass


class LeApiQueryError(LeApiError):
    pass


##@brief Handles mulitple query errors
class LeApiQueryErrors(LodelExceptions, LeApiQueryError):
    pass
