from flask.sessions import SessionInterface
import os
import re
from lodel.session.lodel_filesystem_session.lodel_filesystem_session import LodelFileSystemSession
from contextlib import suppress
import binascii


class LodelFileSystemSessionInterface(SessionInterface):
    
    __sessions = dict()
    
    def __init__(self, directory):
        self.directory = os.path.abspath(directory)
        os.makedirs(self.directory, exist_ok=True)
    
    def open_session(self, app, request):
        self.filename_template = app.config['lodel.filesystem_sessions']['filename_template']
        self.session_tokensize = int(app.config['lodel.sessions']['tokensize'])
        self.clean_sessions()
        sid = request.cookies.get(app.session_cookie_name) or self.generate_token() #or '{}-{}'.format(uuid1(), os.getpid())
        if self.__class__.__sessions.get(sid, None) is None:
            self.__class__.__sessions[sid] = self.generate_file_path(sid, self.filename_template)
        return LodelFileSystemSession(self.directory, sid)
    
    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        
        if not session:
            with suppress(FileNotFoundError):
                os.unlink(session.path)
                del(self.__class__.__sessions[session.sid])
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        
        cookie_exp = self.get_expiration_time(app, session)
        response.set_cookie(app.session_cookie_name, session.sid, expires=cookie_exp, httponly=False,
                            domain=domain)

    def generate_file_path(self, sid, filename_template):
        return os.path.abspath(os.path.join(self.directory, filename_template) % sid)
    
    ## @brief Retrieves the token from the file system
    #
    # @param filepath str
    # @return str|None : returns the token or None if no token was found
    def get_token_from_filepath(self, filepath):
        token_regex = re.compile(os.path.abspath(os.path.join(self.directory, self.filename_template % '(?P<token>.*)')))
        token_search_result = token_regex.match(filepath)
        if token_search_result is not None:
            return token_search_result.groupdict()['token']
        return None
    
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
    
    ## @brief Cleans the sessions' store by deleting the expired sessions' files
    # @todo add logging to the cleaning action
    def clean_sessions(self):
        # Unregistered files in the sessions directory
        session_files_directory = os.path.abspath(self.directory)
        for session_file in [file_path for file_path in os.listdir(session_files_directory) if os.path.isfile(os.path.join(session_files_directory, file_path))]:
            session_file_path = os.path.join(session_files_directory, session_file)
            token = self.get_token_from_filepath(session_file_path)
            if token is None or self.__class__.__sessions.get(token, None) is None:
                os.unlink(session_file_path)