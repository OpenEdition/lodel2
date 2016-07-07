from lodel.auth.auth import Client

class WebUiClient(Client):
    
    def __init__(self, ip, user_agent):
        self.__ip = ip
        self.__user_agent = user_agent
        super().__init__()

    def __str__(self):
        return "%s (%s)" % (self.__ip, self.__user_agent)
