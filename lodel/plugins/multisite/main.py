#Known bugs : 
#Sockets are not closed properly leading in a listening socket leak, a patch
#will be submitted for cpython 3.6
#

import os
import sys
import signal
import socket
import socketserver
import wsgiref
import wsgiref.simple_server
from wsgiref.simple_server import make_server
from io import BufferedWriter

from lodel.context import LodelContext
from lodel.context import ContextError


from multiprocessing.pool import Pool
import multiprocessing

##@brief Set the poll interval to detect shutdown requests (do not work)
SHUTDOWN_POLL_INTERVAL = 0.1 # <-- No impact because of ForkingTCPServer bug

##@brief Stores the signal we uses to kill childs
KILLING_CHILDS_SIGNAL = signal.SIGTERM

FAST_APP_EXPOSAL_CACHE = dict()

##@brief Reimplementation of WSGIRequestHandler
#
#Handler class designed to be called by socketserver child classes to handle
#a request.
#We inherit from wsgiref.simple_server.WSGIRequestHandler to avoid writing
#all the construction of the wsgi variables
class LodelWSGIHandler(wsgiref.simple_server.WSGIRequestHandler):
    
    ##@brief Method called by the socketserver to handle a request
    def handle(self):
        #Register a signal handler for sigint in the child process
        req_ref = self.request
	#Dirty copy & past from Lib/http/server.py in Cpython sources
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return
            #Here begin custom code
            env = self.get_environ()
            stdout = BufferedWriter(self.wfile)
            try:
                handler = wsgiref.handlers.SimpleHandler(
                    self.rfile, stdout, self.get_stderr(), env)
                handler.request_handler = self      # backpointer for logging
                handler.run(self.server.get_app())
            finally:
                stdout.detach()
        except socket.timeout as e:
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return
    
    ##@brief An attempt to solve the socket leak problem
    def close(self):
        self.request.close()
        super().close()

##@brief ForkMixIn using multiprocessing.pool.Pool
class PoolMixIn:

    pool_size = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pool = Pool(self.__class__.pool_size)
        self.__results = list()

    def __pool_callback(self, request, client_address):
        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
            pass
        except:
            try:
                self.handle_error(request, client_address)
                self.shutdown_request(request)
            finally:
                pass

    def collect_results(self):
        new_res = list()
        while len(self.__results) > 0:
            cur = self.__results.pop()
            try:
                cur.get(0.0)
            except multiprocessing.TimeoutError:
                new_res.append(cur)
        self.__results = new_res

    def process_request(self, request, client_address):
        self.collect_results()
        res = self.__pool.apply_async(
            self.__pool_callback, (self, request, client_address))
        self.__results.append(res)
        self.close_request(request)
        return

    def shutdown(self):
        print("Terminating jobs")
        self.__pool.terminate()
        print("Waiting jobs to end...")
        self.__pool.join()
 

##@brief WSGIServer implementing ForkingTCPServer.
#
#Same features than wsgiref.simple_server.WSGIServer but process each requests
#in a child process
class ForkingWSGIServer(
        wsgiref.simple_server.WSGIServer, PoolMixIn):
    
    ##@brief static property indicating the max number of childs allowed
    max_children = 40
    request_queue_size = 40
    allow_reuse_address = True

##@brief utility function to extract site id from an url
def site_id_from_url(url):
    res = ''
    for c in url[1:]:
        if c == '/':
            break
        res += c
    if len(res) == 0:
        return None
    return res

##@brief Utility function to return quickly an error
def http_error(env, start_response, status = '500 internal server error', \
        extra = None):
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    msg = status
    if extra is not None:
        msg = extra
    return [msg.encode('utf-8')]

##@brief This method is run in a child process by the handler
def wsgi_router(env, start_response):
    #Attempt to load a context
    site_id = site_id_from_url(env['PATH_INFO'])
    if site_id is None:
        #It can be nice to provide a list of instances here
        return http_error(env, start_response, '404 Not Found')
    try:
        LodelContext.set(site_id)
        #We are in the good context

    except ContextError as e:
        print(e)
        return http_error(env, start_response, '404 Not found',
            "No site named '%s'" % site_id)
    #Calling webui
    return FAST_APP_EXPOSAL_CACHE[site_id].application(env, start_response)
    #LodelContext.expose_modules(globals(), {
    #    'lodel.plugins.webui.run': ['application']})
    #return application(env, start_response)

##@brief Starts the server until a SIGINT is received
def main_loop():
    multiprocessing.set_start_method('forkserver')
    LodelContext.expose_modules(globals(), {'lodel.settings': ['Settings']})
    ForkingWSGIServer.pool_size = Settings.server.max_children
    listen_addr = Settings.server.listen_address
    listen_port = Settings.server.listen_port
    server = wsgiref.simple_server.make_server(
        listen_addr, listen_port, wsgi_router,
        server_class=ForkingWSGIServer, handler_class = LodelWSGIHandler)
    #Signal handler to close server properly on sigint
    def sigint_handler(signal, frame):
        print("Ctrl-c pressed, exiting")
        #server.shutdown()
        server.server_close()
        exit(0)
    signal.signal(signal.SIGINT, sigint_handler)
    #Listen until SIGINT
    server.serve_forever(SHUTDOWN_POLL_INTERVAL)

