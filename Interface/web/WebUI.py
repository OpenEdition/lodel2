# -*- coding: utf-8 -*-

from Interface.Interface import Interface

## @brief Web Interface Manager
class WebUI(Interface):

    ## @brief Constructor
    #
    # @param request dict : request informations got from the server
    def __init__(self, request):
        super(WebUI).__init__(request)

    def response(self):
        pass
