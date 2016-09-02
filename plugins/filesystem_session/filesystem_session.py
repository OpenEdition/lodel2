# -*- coding: utf-8 -*-


class FileSystemSession(dict):

    def __init__(self, token):
        self.__token = token
        self.__path = None

    @property
    def token(self):
        return self.__token

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        self.__path = path
