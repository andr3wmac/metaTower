"""
 * metaTower v0.3.5
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew W. MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import socket, thread, os, time, sys, Cookie, uuid, hashlib, mtAuth, mimetypes, threading, base64
import mtSession, mtHTTPProcessor
import mtCore as mt

class HTTPOut():
    class mtEntry():
        def __init__(self):
            self.html = False
            self.css = False
            self.js = False
            self.data = ""
            self.target = ""

    def __init__(self):
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
        
    def htmlFile(self, filename, target="body", append=False): self.html(self._getFileContents(filename), target, append)
    def html(self, data, target="body", append = False):
        newEntry = HTTPOut.mtEntry()
        newEntry.data = data
        
        if ( append ): newEntry.target = "+" + target
        else: newEntry.target = target
        
        newEntry.html = True
        self.mt_entrys.append(newEntry)

    def file(self, filepath, home_folder = "packages"):
        self.binary_entry = os.path.join(home_folder, filepath)
        
    def text(self, data):
        self.text_entry += data
        
    def _getFileContents(self, filepath, home_folder = "packages"):
        filepath = os.path.join(home_folder, filepath)
        if ( os.path.isfile(filepath) ):
            f = open(filepath, "rb")
            return str(f.read())
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
            if ( not self.headers.has_key("Content-Type") ): 
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
            f = open(self.binary_entry, "rb")
            f.seek(self.binary_start)

            while (self.binary_start <= self.binary_end):
                chunk_size = 4096
                if ( (self.binary_start+chunk_size) > (self.binary_end) ): chunk_size = (self.binary_end-self.binary_start)+1

                chunk = f.read(chunk_size)
                if not chunk: break
                socket.send(chunk)
                self.binary_start += len(chunk)
        else:
            socket.send(content)

class HTTPHandler(threading.Thread):
    def __init__(self, client_socket, client_addr):
        threading.Thread.__init__(self)
        self.daemon = True
        self.client_socket = client_socket
        self.client_addr = client_addr

    def run(self):
        try:
            output = None
            local_ip, local_port = self.client_socket.getpeername()
            other_ip, other_port = self.client_socket.getsockname()
            mt.log.info("Connection opened by " + str(self.client_addr[0]))
            
            keep_alive = True
            while keep_alive:
                # receive and split the data.
                data = self.client_socket.recv(1024)
                if not data: break
                lines = data.rstrip().splitlines(False)

                # process the data into a managable form.
                output = HTTPOut()

                request_type = "unknown"
                request_path = ""
                post_data = ""
                cookies = {}
                header_only = False
                auth_line = ""

                for line in lines:
                    args = line.split(" ")

                    if ( args[0] == "GET" ) or ( args[0] == "POST" ):
                        request_type = args[0]
                        request_path = args[1]
                        output.http_version = args[2]

                    if ( args[0] == "HEAD" ):
                        request_type = "GET"
                        request_path = args[1]
                        output.http_version = args[2]
                        header_only = True

                    if ( args[0] == "Cookie:" ):
                        cookiedata = line[8:].split(";")
                        for cookie in cookiedata:
                            cookieargs = cookie.split("=")
                            cookies[cookieargs[0].lstrip()] = cookieargs[1]

                    if ( args[0] == "Content-Type:" ):
                        if ( args[1] == "multipart/form-data;" ):
                            boundary_args = args[2].split("=")
                            if ( boundary_args[0] == "boundary" ):
                                while post_data == "":
                                    boundary_data = data.split(boundary_args[1])
                                    if ( len(boundary_data) < 4 ): 
                                        data += self.client_socket.recv(1024)
                                    else:
                                        post_data = data.split(boundary_args[1])[2]
                        if ( args[1] == "application/x-www-form-urlencoded" ):
                            # this needs to be updated later.                
                            data += self.client_socket.recv(1024)
                            post_data = data.split("\r\n\r\n")[1]

                    if ( args[0] == "Connection:"):
                        if ( args[1].lower() != "keep-alive" ):
                            keep_alive = False
                        connection = args[1]

                    if ( args[0] == "Range:"):
                        byte_range = args[1].split("=")[1].split("-")
                        if ( byte_range[0] != "" ): output.binary_start = int(byte_range[0])
                        if ( byte_range[1] != "" ): output.binary_end = int(byte_range[1])

                    if (( args[0] == "Authorization:" ) and ( len(args) == 3 )):
                        auth_line = base64.b64decode(args[2])

                    if ( args[0] == "" ):
                        break
            
                # clean the path
                request_path = request_path.replace("%20", " ")
                request_path = request_path.replace("%22", '"')
                request_path = request_path.replace("%27", "'")

                # check to see if we have a session cookie and if its valid.    
                try:    
                    # filekeys are one time use, external, check for that
                    if ( request_path[:2] == "/*" ):
                        key = request_path[2:]
                        fkey = mtSession.fileKey(key)
                        if ( fkey != None ):
                            output.file(fkey, "")
                        else:
                            output.text("Expired or invalid.")
                    else:
                        session = None
                        if ( "session" in cookies ): 
                            session = mtSession.findSession(cookies["session"])
                        if ( session == None ):
                            output.append(mtHTTPProcessor.processLogin(self.client_socket, request_path, auth_line))
                        else:
                            # keep session IP up to date.
                            session.IP = self.client_addr[0]

                            # check for a dirty url ( login when a cookie exists )
                            if ( request_path.startswith("/?") ):
                                output.append(session.cleanRedirect())
                            else:
                                output.append(mtHTTPProcessor.processRequest(session, request_type, request_path, post_data))
                except Exception as inst:
                    raise
                    mt.log.error("Login: " + str(inst.args))
                    keep_alive = False

                # Process output.
                try:
                    if ( output != None ):
                        if ( type(output).__name__ == 'instance' ) and ( output.__class__ is HTTPOut ):
                            output.send(self.client_socket, header_only)
                        else:
                            out = session.out()
                            out.text(str(output))
                            out.send(self.client_socket, header_only)

                except Exception as inst:
                    mt.log.error("Sending packet: " + str(inst.args))
                    keep_alive = False

        except Exception as inst:
            mt.log.error("Socket error: " + str(inst.args))
        finally:
            self.client_socket.close()

class HTTPServer( threading.Thread ):
    def run ( self ):
        config = mt.config
        addr = ("", int(config["port"]))
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(addr)
        server_socket.listen(10)
        server_socket.settimeout(1)
    
        while mt.running:
            try:
                client_socket, client_addr = server_socket.accept()
                client_socket.setblocking(1)
                client_thread = HTTPHandler(client_socket, client_addr)
                client_thread.start()
            except socket.timeout:
                pass
        server_socket.shutdown(1)

def start():
    http = HTTPServer()
    http.daemon = True
    http.start()
