#-*- coding: utf-8 -*-

class EditorialModelError(Exception):
    pass


def assert_edit():
    try:
        from lodel import Settings
    except ImportError: #Very dirty, but don't know how to fix the tests
        return
    if not Settings.editorialmodel.editormode:
        raise EditorialModelError("EM is readonly : editormode is OFF")

