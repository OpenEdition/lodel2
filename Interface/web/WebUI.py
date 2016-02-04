# -*- coding: utf-8 -*-

from .controllers import *


## @brief Web Interface Manager
class WebUI(object):

    ## @brief Constructor
    #
    # @param request dict : request informations got from the server
    def __init__(self, request):
        self.request = self.parse_request(request)

    ## @brief parses the request informations received from the application
    #
    # @param request dict
    # @return dict
    def parse_request(self, request):
        uri_args = request['REQUEST_URI'].split('/')
        uri_args.pop(0)  # We delete the first element which is a ""
        request['URL_ARGS'] = uri_args
        return request

    def response(self):
        print(self.request['URL_ARGS'])
        if self.request['URL_ARGS'][0] == 'admin':
            return admin(self.request)
        else:
            return "Hello World"
