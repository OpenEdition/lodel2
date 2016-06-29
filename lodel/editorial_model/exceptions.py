#-*- coding: utf-8 -*-

class EditorialModelError(Exception):
    pass


def assert_edit():
    from lodel import Settings
    if not Settings.editorialmodel.editormode:
        raise EditorialModelError("EM is readonly : editormode is OFF")

