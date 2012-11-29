"""
 * metaTower v0.4.5
 * http://www.metatower.com
 *
 * Copyright 2012, Andrew Mac
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import mt, socket
from HTTPServer import HTTPServer

def onLoad():
    if ( start() ):
        print "HTTP started."
    else:
        print "HTTP failed to start."

#def onUnload():
#    running = False 

files = {}
def addFile(request, filepath):
    global files
    files[request] = filepath
    mt.events.register("HTTP GET " + request, getFile)
    mt.events.register("HTTP HEAD " + request, getFile)

def getFile(httpIn, httpOut):
    global files
    if ( files.has_key(httpIn.path) ):    
        httpOut.file(files[httpIn.path])    

def start():
    global http_thread
    try:
        addr = ("", int(mt.config["port"]))
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(addr)
        server_socket.listen(10)
        server_socket.settimeout(0.1)

        http_thread = HTTPServer(server_socket)
        http_thread.start()
        return True

    except Exception as inst:
        pass

    return False

