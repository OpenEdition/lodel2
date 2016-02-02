#-*- coding: utf-8 -*-

import os

import EditorialModel
from leapi.lecrud import _LeCrud

class AclFactory(object):
    
    def __init__(self, code_filename = 'acl/dyn.py'):
        self._code_filename = code_filename
        self._dyn_file = os.path.basename(code_filename)
        self._modname = os.path.dirname(code_filename).strip('/').replace('/', '.') #Warning Windaube compatibility

    ## @brief Create dynamic code python file
    # @param modle Model : An editorial model
    # @param leap_dyn_module_name str : Name of leapi dynamic module name
    def create_pyfile(self, model, leapi_dyn_module_name):
        with open(self._code_filename, "w+") as dynfp:
            dynfp.write(self.generate_python(model, leapi_dyn_module_name))

    def generate_python(self, model, leapi_module_name):
        result = """## @author acl/factory

from acl.acl import get_wrapper
"""
        
        classes_to_wrap = ['LeCrud', 'LeObject', 'LeClass', 'LeType', 'LeRelation', 'LeHierarch', 'LeRel2Type']
        classes_to_wrap += [ _LeCrud.name2classname(emclass.name) for emclass in model.components(EditorialModel.classes.EmClass) ]
        classes_to_wrap += [ _LeCrud.name2classname(emtype.name) for emtype in model.components(EditorialModel.types.EmType) ]

        for class_to_wrap in classes_to_wrap:
            result += """
## @brief Wrapped for {class_to_wrap} LeAPI class
# @see {module_name}.{class_to_wrap}
class {class_to_wrap}(get_wrapper('{module_name}', '{class_to_wrap}')):
    pass

""".format(
            class_to_wrap = class_to_wrap,
            module_name = leapi_module_name
        )
        return result
