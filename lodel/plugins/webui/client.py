from lodel.context import LodelContext
LodelContext.expose_modules(globals(), {'lodel.auth.client': ['Client']})

class WebUiClient(Client):
    
    def __init__(self, ip, user_agent, session_token = None):
        self.__ip = ip
        self.__user_agent = user_agent
        super().__init__(session_token = session_token)

    def __str__(self):
        return "%s (%s)" % (self.__ip, self.__user_agent)
