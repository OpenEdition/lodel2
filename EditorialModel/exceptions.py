# -*- coding: utf-8 -*-

## @brief An exception class to tell that a component don't exist
class EmComponentNotExistError(Exception):
    pass

## @brief Raised on uniq constraint error at creation
# This exception class is dedicated to be raised when create() method is called
# if an EmComponent with this name but different parameters allready exist
class EmComponentExistError(Exception):
    pass

## @brief An exception class to tell that no ranking exist yet for the group of the object
class EmComponentRankingNotExistError(Exception):
    pass

## @brief An exception class to return a failure reason for EmComponent.check() method
class EmComponentCheckError(Exception):
    pass
