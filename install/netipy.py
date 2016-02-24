#!/usr/bin/python3
#-*- coding: utf-8 -*-

#
# A server that provide access to interactive python interpreter through network
#
# This is a demo implementation of a Lodel2 interface

import socket
import threading
import subprocess
import time
import sys
import signal

PORT = 1337
#BIND = None
BIND = 'localhost'
THREAD_COUNT = 10
SOCK_TIMEOUT = 5

servsock = None # Stores the server socket in order to close it when exception is raised


# Thread function called when client connected
def client_thread(sock, addr):
    # Starting interactive Lodel2 python in a subprocess
    sock.setblocking(True)
    sock_stdin = sock.makefile(mode='r', encoding='utf-8', newline="\n")
    sock_stdout = sock.makefile(mode='w', encoding='utf-8', newline="\n")

    ipy = subprocess.Popen(['python', 'netipy_loader.py', addr[0]], stdin=sock_stdin, stdout=sock_stdout, stderr=sock_stdout)
    ipy.wait()
    sock.close()
    return True

# Main loop
def main():
    servsock = socket.socket(family = socket.AF_INET, type=socket.SOCK_STREAM)
    servsock.settimeout(5)
    bind_addr = socket.gethostname() if BIND is None else BIND
    servsock.bind((bind_addr, PORT))
    servsock.listen(5)
    globals()['servsock'] = servsock

    threads = list()
    
    print("Server listening on %s:%s" % (bind_addr, PORT))
    while True:
        # Accept if rooms left in threads list
        if len(threads) < THREAD_COUNT:
            try:
                (clientsocket, addr) = servsock.accept()
                print("Client connected : %s" % addr[0])
                thread = threading.Thread(target = client_thread, kwargs = {'sock': clientsocket, 'addr': addr})
                threads.append(thread)
                thread.start()
            except socket.timeout:
                pass

        # Thread cleanup
        for i in range(len(threads)-1,-1,-1):
            thread = threads[i]
            thread.join(0.1)  #useless ?
            if not thread.is_alive():
                print("Thread %d exited" % i)
                threads.pop(i)
 
# Signal handler designed to close socket when SIGINT
def sigint_sock_close(signal, frame):
    if globals()['servsock'] is not None:
        globals()['servsock'].close()
    print("\nCtrl+c pressed, exiting...")
    exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_sock_close)
    try:
        main()
    except Exception as e:
        if globals()['servsock'] is not None:
            globals()['servsock'].close()
        raise e
        

    

    
