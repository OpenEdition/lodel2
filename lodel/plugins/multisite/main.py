#Known bugs : 
#Sockets are not closed properly leading in a listening socket leak
#


import wsgiref
import wsgiref.simple_server
from wsgiref.simple_server import make_server
import http.server
import multiprocessing as mp
import socketserver
import socket
import os
from io import BufferedWriter
import urllib
import threading

import sys, signal

from lodel.context import LodelContext
from lodel.context import ContextError

LISTEN_ADDR = ''
LISTEN_PORT = 1337

SHUTDOWN_POLL_INTERVAL = 0.1

class HtppHandler(wsgiref.simple_server.WSGIRequestHandler):
    def handle(self):
        print("addr : %s %s\n" % (self.client_address, type(self.request)))
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

    ##@brief Copy of wsgiref.simple_server.WSGIRequestHandler.get_environ method
    def get_environ(self):
        env = self.server.base_environ.copy()
        env['SERVER_PROTOCOL'] = self.request_version
        env['SERVER_SOFTWARE'] = self.server_version
        env['REQUEST_METHOD'] = self.command
        if '?' in self.path:
            path,query = self.path.split('?',1)
        else:
            path,query = self.path,''

        env['PATH_INFO'] = urllib.parse.unquote(path, 'iso-8859-1')
        env['QUERY_STRING'] = query

        host = self.address_string()
        if host != self.client_address[0]:
            env['REMOTE_HOST'] = host
        env['REMOTE_ADDR'] = self.client_address[0]

        if self.headers.get('content-type') is None:
            env['CONTENT_TYPE'] = self.headers.get_content_type()
        else:
            env['CONTENT_TYPE'] = self.headers['content-type']

        length = self.headers.get('content-length')
        if length:
            env['CONTENT_LENGTH'] = length

        for k, v in self.headers.items():
            k=k.replace('-','_').upper(); v=v.strip()
            if k in env:
                continue                    # skip content length, type,etc.
            if 'HTTP_'+k in env:
                env['HTTP_'+k] += ','+v     # comma-separate multiple headers
            else:
                env['HTTP_'+k] = v
        return env

##@brief Speciallized ForkingTCPServer to fit specs of WSGIHandler
class HttpServer(socketserver.ForkingTCPServer):
    
    ##@brief Max childs count
    max_children = 80

    ##@brief Onverwritting of ForkingTCPServer.server_bind method
    #to fit the wsgiref specs
    def server_bind(self):
        super().server_bind()
        #Copy & paste from Lib/http/server.py
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # Copy&paste from Lib/wsgiref/simple_server.py
        # Set up base environment 
        env = self.base_environ = {}
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.server_port)
        env['REMOTE_HOST']=''
        env['CONTENT_LENGTH']=''
        env['SCRIPT_NAME'] = ''

    ##@brief Hardcoded callback function
    def get_app(self):
        return wsgi_router

    ##@brief An attempt to solve the socket leak problem
    def close_request(self, request):
        print("Closing client socket in server : %s" % request)
        request.close()

    ##@brief An attempt to solve the socket leak problem
    def server_close(self):
        print("Closing listening socket")
        self.socket.close()

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
    #
    #   Here we have to put the code that run the request
    #
    
    #Testing purpose
    rep = "Woot '%s'" % site_id
    print(rep)
    start_response('200 ok', [('Content-type', 'text/plain; charset=utf-8')])
    return [rep.encode('utf-8')]

    #mp.Process(target=foo, args=(env,start_response))
    return child_proc(env, start_response)

def main_loop():
    
    #Set the start method for multiprocessing
    mp.set_start_method('forkserver')
    print("\n\nPID = %d\n\n" % os.getpid())

    listen_addr = LISTEN_ADDR
    listen_port = LISTEN_PORT
    
    #server = socketserver.ForkingTCPServer((listen_addr, listen_port),
    #    HtppHandler)
    server = HttpServer((listen_addr, listen_port),
        HtppHandler)
    
    #Signal handler to close server properly on sigint
    def sigint_handler(signal, frame):
        print("Ctrl-c pressed, exiting")
        server.shutdown() # <-- Do not work for unkonwn reasons
        server.server_close()
        sys.exit(0)
    #signal.signal(signal.SIGINT, sigint_handler)

    server.serve_forever(SHUTDOWN_POLL_INTERVAL)

