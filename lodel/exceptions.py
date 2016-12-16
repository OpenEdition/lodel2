#-*- coding: utf-8 -*-

class LodelException(Exception):
    pass

class LodelExceptions(LodelException):
    ##@brief Instanciate a new exceptions handling multiple exceptions
    # @param msg str : Exception message
    # @param exceptions dict : A list of data check Exception with concerned field (or stuff) as key
    def __init__(self, msg = "Unknow error", exceptions = None):
        self._msg = msg
        self._exceptions = dict() if exceptions is None else exceptions

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        msg = self._msg
        for_iter = self._exceptions.items() if isinstance(self._exceptions, dict) else enumerate(self.__exceptions)
        for obj, expt in for_iter:
            msg += "\n\t{expt_obj} : ({expt_name}) {expt_msg}; ".format(
                    expt_obj = obj,
                    expt_name=expt.__class__.__name__,
                    expt_msg=str(expt)
            )
        return msg

##@brief Designed to be a non catched exception.
#
#@note Designed to be raised in dramatic case
class LodelFatalError(Exception):
    pass

##@brief Designed to be a catched exception.
#
#@note Designed to be raised in DataHandler
class DataNoneValid(Exception):
    pass
    
##@brief Designed to be a catched exception.
#
#@note Designed to be raised in DataHandler
class FieldValidationError(Exception):
    pass

