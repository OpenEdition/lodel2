from flask.sessions import SessionInterface
import binascii
import os
from lodel.session.lodel_ram_session.lodel_ram_session import LodelRamSession
import copy


class LodelRamSessionInterface(SessionInterface):
    __sessions = dict()
    
    def open_session(self, app, request):
        self.session_tokensize = int(app.config['lodel.sessions']['tokensize'])
        sid = request.cookies.get(app.session_cookie_name) or self.generate_token()
        session = LodelRamSession(sid)
        if self.__class__.__sessions.get(sid, None) is None:
            self.__class__.__sessions[sid] = session 
        return session

    
    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        
        if not session:
            del(self.__class__.__sessions[session.sid])
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        
        cookie_exp = self.get_expiration_time(app, session)
        response.set_cookie(app.session_cookie_name, session.sid, expires=cookie_exp, httponly=False, domain=domain)
    
    ## @brief generates a new session token
    #
    # @return str
    #
    # @remarks There is no valid reason for checking the generated token uniqueness:
    #        - checking for uniqueness is slow ;
    #        - keeping a dict with a few thousand keys of hundred bytes also is
    #            memory expensive ;
    #        - should the system get distributed while sharing session storage, there
    #            would be no reasonable way to efficiently check for uniqueness ;
    #        - sessions do have a really short life span, drastically reducing
    #            even more an already close to inexistent risk of collision. A 64 bits
    #            id would perfectly do the job, or to be really cautious, a 128 bits
    #            one (actual size of UUIDs) ;
    #        - if we are still willing to ensure uniqueness, then simply salt it
    #            with a counter, or a timestamp, and hash the whole thing with a 
    #            cryptographically secured method such as sha-2 if we are paranoids
    #            and trying to avoid what will never happen, ever ;
    #        - sure, two hexadecimal characters is one byte long. Simply go for 
    #            bit length, not chars length.
    def generate_token(self):
        token = binascii.hexlify(os.urandom(self.session_tokensize))
        if self.__class__.__sessions.get(token, None) is not None:
            token = self.generate_token()
        return token.decode('utf-8')
    
    