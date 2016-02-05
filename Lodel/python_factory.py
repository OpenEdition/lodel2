#-*- coding: utf-8 -*-

import os

## @brief Abstract class designed to generate python code files
# @note implemented by leapi.lefactory.LeFactory and acl.factory.AclFactory classes
class PythonFactory(object):
    
    ## @brief Instanciate the generator
    # @param code_filename str : the output filename for python code
    def __init__(self, code_filename):
        if self.__class__ == PythonFactory:
            raise NotImplementedError("Abtract class")
        self._code_filename = code_filename
        self._dyn_file = os.path.basename(code_filename)
        self._modname = os.path.dirname(code_filename).strip('/').replace('/', '.') #Warning Windaube compatibility
        
    ## @brief Create dynamic code python file
    # @param *args : positional arguments forwarded to generate_python() method
    # @param **kwargs : named arguments forwarded to generate_python() method
    def create_pyfile(self, *args, **kwargs):
        with open(self._code_filename, "w+") as dynfp:
            dynfp.write(self.generate_python(*args, **kwargs))
    
    def generate_python(self, *args, **kwargs):
        raise NotImplemented("Abtract method")
