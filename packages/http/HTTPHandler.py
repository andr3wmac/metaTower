import mt, processor, sessions, urllib
from mt import threads
from HTTPIn import HTTPIn
from HTTPOut import HTTPOut

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

                    if ( args[0] == "Host:" ):
                        httpIn.host = args[1]

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

                # clean the path of url garbage
                httpIn.path = urllib.unquote(httpIn.path)

                # check to see if we have a session cookie and if its valid.    
                try:    
                    # filekeys are one time use, external, check for that
                    if ( httpIn.path[:2] == "/*" ):
                        key = httpIn.path[2:]
                        fkey = sessions.fileKey(key)
                        if ( fkey != None ):
                            output.file(fkey)
                        else:
                            output.text("Expired or invalid.")
                    else:
                        if ( "session" in httpIn.cookies ): 
                            httpIn.session = sessions.find(httpIn.cookies["session"])
                            output.session = httpIn.session

                        if ( httpIn.session == None ):
                            processor.processLogin(self.client_socket, httpIn, output)
                        else:
                            # keep session IP up to date.
                            httpIn.session.IP = self.client_addr[0]

                            # check for a dirty url ( login when a cookie exists )
                            if ( httpIn.path.startswith("/?") ):
                                output.status = "302 Found"
                                output.headers["Location"] = "http://" + httpIn.host + "/"
                                output.headers["Content-Length"] = "0"
                            else:
                                processor.processRequest(httpIn, output)
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

