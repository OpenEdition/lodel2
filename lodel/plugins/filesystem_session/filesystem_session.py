# -*- coding: utf-8 -*-


## @brief An extended dictionary representing a session in the file system
class FileSystemSession(dict):

    ## @brief Constructor
    # @param token str
    def __init__(self, token):
        self.__token = token
        self.__path = None

    ## @brief token getter
    # @return str
    @property
    def token(self):
        return self.__token

    ## @brief path getter
    # @return str
    @property
    def path(self):
        return self.__path

    ## @brief path setter
    # @param path str
    @path.setter
    def path(self, path):
        self.__path = path
