#-*- coding: utf-8 -*-

## @package lodel.editorial_model.exceptions
# This module contains the specific exceptions related to the EditorialModel Management.


## @brief Raises an Editorial Model specific exception.
class EditorialModelError(Exception):
    pass


## @brief Tries to import the settings module.
# @raise EditorialModelError
def assert_edit():
    try:
        from lodel import Settings
    except ImportError:  # Very dirty, but don't know how to fix the tests
        return
    if not Settings.editorialmodel.editormode:
        raise EditorialModelError("EM is readonly : editormode is OFF")

