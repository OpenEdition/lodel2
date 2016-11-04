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

##@brief On wich addr we want to bind. '' mean all interfaces
LISTEN_ADDR = ''
##@brief Listening socket port
LISTEN_PORT = 1337

##@brief Set the poll interval to detect shutdown requests (do not work)
SHUTDOWN_POLL_INTERVAL = 0.1 # <-- No impact because of ForkingTCPServer bug

##@brief Stores the signal we uses to kill childs
KILLING_CHILDS_SIGNAL = signal.SIGTERM

##@brief Reimplementation of WSGIRequestHandler
#
#Handler class designed to be called by socketserver child classes to handle
#a request.
#We inherit from wsgiref.simple_server.WSGIRequestHandler to avoid writing
#all the construction of the wsgi variables
class LodelWSGIHandler(wsgiref.simple_server.WSGIRequestHandler):
    
    ##@brief Method called by the socketserver to handle a request
    def handle(self):
        print("addr : %s %s\n" % (self.client_address, type(self.request)))
        #Register a signal handler for sigint in the child process
        req_ref = self.request
        def sigstop_handler_client(signal, frame):
            req_ref.close()
            print("Client %d stopping by signal" % os.getpid())
            os._exit(0)
        signal.signal(KILLING_CHILDS_SIGNAL, sigstop_handler_client)
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
        print("Closing request from handler : %s" % self.request)
        self.request.close()
        super().close()

##@brief WSGIServer implementing ForkingTCPServer.
#
#Same features than wsgiref.simple_server.WSGIServer but process each requests
#in a child process
class ForkingWSGIServer(
        wsgiref.simple_server.WSGIServer, socketserver.ForkingTCPServer):
    ##@brief Custom reimplementation of shutdown method in order to ensure
    #that we close all listening sockets
    #
    #This method is here because of a bug (or a missing feature) : 
    #The socketserver implementation force to call the shutdown method
    #from another thread/process else it leads in a deadlock.
    #The problem is that the implementation of shutdown set a private attribute
    #__shutdown_request to true. So we cannot reimplement a method that will
    #just set the flag to True, we have to manually collect each actives 
    #childs. A patch is prepared and will be proposed for cpython upstream.
    def shutdown(self):
        if self.active_children is not None:
            for pid in self.active_children.copy():
                print("Killing : %d"%pid)
                os.kill(pid, KILLING_CHILDS_SIGNAL)
                try:
                    pid, _ = os.waitpid(pid, 0)
                    self.active_children.discard(pid)
                except ChildProcessError:
                    self.active_children.discard(pid)
        self.server_close()

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
    print("\n\nCPROCPID = %d\n\n" % os.getpid()) #<-- print PID (for debug)
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
    LodelContext.expose_modules(globals(), {
        'lodel.plugins.webui.run': ['application']})
    return application(env, start_response)

##@brief Starts the server until a SIGINT is received
def main_loop():
    print("PID = %d" % os.getpid())

    listen_addr = LISTEN_ADDR
    listen_port = LISTEN_PORT
    server = wsgiref.simple_server.make_server(
        listen_addr, listen_port, wsgi_router,
        server_class=ForkingWSGIServer, handler_class = LodelWSGIHandler)
    #Signal handler to close server properly on sigint
    def sigint_handler(signal, frame):
        print("Ctrl-c pressed, exiting")
        server.shutdown()
        server.server_close()
        exit(0)
    signal.signal(signal.SIGINT, sigint_handler)
    #Listen until SIGINT
    server.serve_forever(SHUTDOWN_POLL_INTERVAL)

