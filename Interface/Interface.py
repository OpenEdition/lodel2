# -*- coding: utf-8 -*-


## @brief Abstract Interface class
class Interface(object):

    def __init__(self, request):
        self.request = self.parse_request(request)

    ## @brief parses the request informations received from the application
    #
    # @param request dict
    # @return dict
    def parse_request(self, request):
        pass

    ## @brief creates the response to send back to the user
    def response(self):
        pass
