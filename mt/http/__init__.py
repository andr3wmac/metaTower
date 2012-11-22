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

import socket, thread, os, time, sys, Cookie, uuid, hashlib, mimetypes, threading, base64
import mt, processor
from mt import threads

running = False

class HTTPIn():
    def __init__(self):
        self.method = "unknown"
        self.path = ""
        self.post_data = ""
        self.cookies = {}
        self.header_only = False
        self.auth_line = ""
        self.user_agent = ""
        self.session = None

class HTTPOut():
    class mtEntry():
        def __init__(self):
            self.html = False
            self.css = False
            self.js = False
            self.data = ""
            self.target = ""

    def __init__(self, session = None):
        self.session = session
        self.http_version = ""
        self.status = ""
        self.cookies = {}
        self.headers = {}
        
        self.mt_entrys = [];
        self.text_entry = "";
        self.binary_entry = "";
        self.binary_start = 0;
        self.binary_end = 0;
        
    def cssFile(self, filename): self.css(self._getFileContents(filename))
    def css(self, data):
        newEntry = HTTPOut.mtEntry()
        newEntry.data = data
        newEntry.css = True
        self.mt_entrys.append(newEntry)
        
    def jsFile(self, filename): self.js(self._getFileContents(filename))
    def js(self, data):
        newEntry = HTTPOut.mtEntry()
        newEntry.data = data
        newEntry.js = True
        self.mt_entrys.append(newEntry)
        
    def htmlFile(self, filename, target="", append=False): self.html(self._getFileContents(filename), target, append)
    def html(self, data, target="", append = False):
        newEntry = HTTPOut.mtEntry()
        newEntry.data = data
        
        if ( append ): newEntry.target = "+" + target
        else: newEntry.target = target
        
        newEntry.html = True
        self.mt_entrys.append(newEntry)

    def file(self, filepath):
        self.binary_entry = filepath
        
    def text(self, data):
        self.text_entry += data
        
    def _getFileContents(self, filepath):
        if ( os.path.isfile(filepath) ):
            f = open(filepath, "rb")
            data = f.read()
            f.close()
            return str(data)
        mt.log.error("404 Not Found: " + filepath)
        self.status = "404 Not Found"
        return None
        
    def append(self, targ):
        if ( targ == None ): return
        
        self.cookies.update(targ.cookies)
        self.headers.update(targ.headers)
        self.mt_entrys.extend(targ.mt_entrys)
        self.text_entry += targ.text_entry

        if ( targ.http_version != "" ): self.http_version = targ.http_version
        if ( targ.status != "" ): self.status = targ.status
        if ( targ.binary_entry != "" ): self.binary_entry = targ.binary_entry

    def send(self, socket, header_only = False):
        content = ""

        socket.settimeout(None)

        if ( self.binary_entry != "" ):
            if ( os.path.isfile(self.binary_entry) ):
                binary_size = os.path.getsize(self.binary_entry)

                if ( self.binary_end == 0 ): self.binary_end = binary_size - 1
                if ( self.binary_start != 0 ) or ( self.binary_end != binary_size - 1 ):
                    self.status = "206 Partial Content"
                    self.headers["Content-Range"] = "bytes " + str(self.binary_start) + "-" + str(self.binary_end) + "/" + str(binary_size)

                self.headers["Content-Type"] = mimetypes.guess_type(self.binary_entry)[0]
                self.headers["Content-Length"] = str(self.binary_end - self.binary_start + 1)
            else:
                mt.log.error("404 Not Found: " + self.binary_entry)
                self.binary_entry = ""
                self.status = "404 Not Found"
                content = "404 Not Found."
                self.headers["Content-Type"] = "text/plain"
                self.headers["Content-Length"] = len(content)
            
        elif ( len(self.mt_entrys) > 0 ):
            self.headers["Cache-Control"] = "no-store"
            locations = ""
            data = ""
            for entry in self.mt_entrys:
                if ( entry.html ):
                    locations += "html:" + str(len(data)) + "," + str(len(entry.data)) + "," + entry.target + ";"
                    data += entry.data
                if ( entry.js ):
                    locations += "js:" + str(len(data)) + "," + str(len(entry.data)) + ";"
                    data += entry.data
                if ( entry.css ):
                    locations += "css:" + str(len(data)) + "," + str(len(entry.data)) + ";"
                    data += entry.data
            content = "!mt:" + str(len(locations)) + ";" + locations + data
            self.headers["Content-Type"] = "text/plain"
            self.headers["Content-Length"] = len(content)
        
        elif ( self.text_entry != "" ):
            if ( not self.headers.has_key("Content-Type") ): 
                self.headers["Content-Type"] = "text/plain"
            if ( not self.headers.has_key("Content-Length") ): 
                self.headers["Content-Length"] = len(self.text_entry)
            content = self.text_entry
        else:
            if ( not self.headers.has_key("Content-Length") ): 
                self.headers["Content-Length"] = 0
            
        # Generate and send the headers.
        if ( self.http_version == "" ): self.http_version = "HTTP/1.1"
        if ( self.status == "" ): self.status = "200 OK"
        headers = self.http_version + " " + self.status + "\r\n"
        for key in self.headers.keys():
            headers += key + ": " + str(self.headers[key]) + "\r\n"
            
        if ( len(self.cookies) > 0 ):
            for key, value in self.cookies.items():    
                headers += "Set-Cookie: " + key + "=" + value + "\r\n"
        headers += "\r\n"
        socket.send(headers)
        if ( header_only ): return

        # send the content.
        if ( self.binary_entry != "" ):
            f = None
            try:
                f = open(self.binary_entry, "rb")
                f.seek(self.binary_start)

                while (self.binary_start <= self.binary_end):
                    chunk_size = 4096
                    if ( (self.binary_start+chunk_size) > (self.binary_end) ): chunk_size = (self.binary_end-self.binary_start)+1

                    chunk = f.read(chunk_size)
                    if not chunk: break
                    socket.send(chunk)
                    self.binary_start += len(chunk)

                f.close()
                f = None
            except Exception as inst:
                mt.log.error("Error reading file:" + str(inst))
            finally:
                if ( f != None ): f.close()
        else:
            socket.send(content)

class HTTPHandler(threads.Thread):
    def __init__(self, client_socket, client_addr):
        threads.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_addr = client_addr

    def run(self):
        try:
            output = None
            local_ip, local_port = self.client_socket.getpeername()
            other_ip, other_port = self.client_socket.getsockname()
            mt.log.info("Connection opened by " + str(self.client_addr[0]))

            keep_alive = True
            #self.client_socket.settimeout(15) # keep-alive timeout of 15 seconds.
            while keep_alive and self.running:
                self.client_socket.settimeout(0.1)

                # attempt to receive, it will timeout after 0.1 seconds.
                try:
                    data = self.client_socket.recv(1024)
                except:
                    continue

                if (not data) or (not self.running): break
                lines = data.rstrip().splitlines(False)

                # create a profile object to track execution time.
                p = mt.utils.profile()

                # process the data into a managable form.
                httpIn = HTTPIn()
                output = HTTPOut()

                for line in lines:
                    args = line.split(" ")

                    if ( args[0] == "GET" ) or ( args[0] == "POST" ):
                        httpIn.method = args[0]
                        httpIn.path = args[1]
                        output.http_version = args[2]

                    if ( args[0] == "HEAD" ):
                        httpIn.method = "GET"
                        httpIn.path = args[1]
                        httpIn.header_only = True
                        output.http_version = args[2]

                    if ( args[0] == "Cookie:" ):
                        cookiedata = line[8:].split(";")
                        for cookie in cookiedata:
                            cookieargs = cookie.split("=")
                            httpIn.cookies[cookieargs[0].lstrip()] = cookieargs[1]

                    if ( args[0] == "User-Agent:" ):
                        httpIn.user_agent = " ".join(args[1:])

                    if ( args[0] == "Content-Type:" ):
                        if ( args[1] == "multipart/form-data;" ):
                            boundary_args = args[2].split("=")
                            if ( boundary_args[0] == "boundary" ):
                                while httpIn.post_data == "":
                                    boundary_data = data.split(boundary_args[1])
                                    if ( len(boundary_data) < 4 ): 
                                        data += self.client_socket.recv(1024)
                                    else:
                                        httpIn.post_data = data.split(boundary_args[1])[2]
                        if ( args[1] == "application/x-www-form-urlencoded" ):
                            # this needs to be updated later.                
                            data += self.client_socket.recv(1024)
                            httpIn.post_data = data.split("\r\n\r\n")[1]

                    if ( args[0] == "Connection:"):
                        if ( args[1].lower() != "keep-alive" ):
                            keep_alive = False
                        connection = args[1]

                    if ( args[0] == "Range:"):
                        byte_range = args[1].split("=")[1].split("-")
                        if ( byte_range[0] != "" ): output.binary_start = int(byte_range[0])
                        if ( byte_range[1] != "" ): output.binary_end = int(byte_range[1])

                    if (( args[0] == "Authorization:" ) and ( len(args) == 3 )):
                        httpIn.auth_line = base64.b64decode(args[2])

                    if ( args[0] == "" ):
                        break
            
                # clean the path
                httpIn.path = httpIn.path.replace("%20", " ")
                httpIn.path = httpIn.path.replace("%22", '"')
                httpIn.path = httpIn.path.replace("%27", "'")
                httpIn.path = httpIn.path.replace("%7B", "{")
                httpIn.path = httpIn.path.replace("%7D", "}")

                # check to see if we have a session cookie and if its valid.    
                try:    
                    # filekeys are one time use, external, check for that
                    if ( httpIn.path[:2] == "/*" ):
                        key = httpIn.path[2:]
                        fkey = mt.sessions.fileKey(key)
                        if ( fkey != None ):
                            output.file(fkey)
                        else:
                            output.text("Expired or invalid.")
                    else:
                        if ( "session" in httpIn.cookies ): 
                            httpIn.session = mt.sessions.find(httpIn.cookies["session"])

                        if ( httpIn.session == None ):
                            output.append(processor.processLogin(self.client_socket, httpIn))
                        else:
                            # keep session IP up to date.
                            httpIn.session.IP = self.client_addr[0]

                            # check for a dirty url ( login when a cookie exists )
                            if ( httpIn.path.startswith("/?") ):
                                output.append(httpIn.session.cleanRedirect())
                            else:
                                output.append(processor.processRequest(httpIn))
                except Exception as inst:
                    raise
                    mt.log.error("Login: " + str(inst.args))
                    keep_alive = False

                # Process output.
                try:
                    if ( output != None ):
                        if ( type(output).__name__ == 'instance' ) and ( output.__class__ is HTTPOut ):
                            output.send(self.client_socket, httpIn.header_only)
                        else:
                            out = httpIn.session.out()
                            out.text(str(output))
                            out.send(self.client_socket, httpIn.header_only)

                except Exception as inst:
                    mt.log.error("Sending packet: " + str(inst.args))
                    keep_alive = False

                p.end([httpIn.path])

        except Exception as inst:
            mt.log.error("Socket error: " + str(inst.args))
        finally:
            if ( self.client_socket ): self.client_socket.close()

class HTTPServer( threads.Thread ):
    def __init__(self, server_socket):
        threads.Thread.__init__(self)
        self.sock = server_socket

    def run ( self ):
        while self.running:
            try:
                client_socket, client_addr = self.sock.accept()
                client_socket.setblocking(1)
                client_thread = HTTPHandler(client_socket, client_addr)
                client_thread.start()
            except socket.timeout:
                pass

        self.sock.shutdown(1)
        self.sock.close()

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

