#-*- coding: utf-8 -*-

import os

import Lodel.python_factory
import EditorialModel
from leapi.lecrud import _LeCrud

## @brief ACL wrapper for leapi dynamically generated classes generator
#
# This class handles dynamic ACL wrapper for dynamically generated leapi classes.
#
# The goal of those wrapped leapi classes is to reroute every calls that are made to
# the API to the acl.acl.ACL module in order to validate them.
class AclFactory(Lodel.python_factory.PythonFactory):
    
    ## @brief Instanciate the generator
    # @param code_filename str : the output filename for python code
    def __init__(self, code_filename = 'acl/dyn.py'):
        super().__init__(code_filename = code_filename)

    ## @brief Generate the python code
    # @param model Model : An editorial model
    # @param leap_dyn_module_name str : Name of leapi dynamically generated module name
    def generate_python(self, model, leapi_module_name):
        result = """## @author acl/factory

from libs.transwrap.transwrap import get_wrapper
import libs.transwrap
from acl.acl import ACL
"""
        
        classes_to_wrap = ['LeCrud', 'LeObject', 'LeClass', 'LeType', 'LeRelation', 'LeHierarch', 'LeRel2Type']
        classes_to_wrap += [ _LeCrud.name2classname(emclass.name) for emclass in model.components(EditorialModel.classes.EmClass) ]
        classes_to_wrap += [ _LeCrud.name2classname(emtype.name) for emtype in model.components(EditorialModel.types.EmType) ]

        for class_to_wrap in classes_to_wrap:
            result += """
## @brief Wrapped for {class_to_wrap} LeAPI class
# @see {module_name}.{class_to_wrap}
class {class_to_wrap}(get_wrapper('{module_name}', '{class_to_wrap}', ACL)):
    pass

""".format(
            class_to_wrap = class_to_wrap,
            module_name = leapi_module_name
        )
        return result
