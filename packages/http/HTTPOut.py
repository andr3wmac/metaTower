import mt, os, mimetypes
from time import strftime

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
        
    # CSS
    def cssFile(self, filename): self.css(self._getFileContents(filename))
    def css(self, data):
        newEntry = HTTPOut.mtEntry()
        newEntry.data = data
        newEntry.css = True
        self.mt_entrys.append(newEntry)
        
    # Javascript
    def jsFunction(self, funcName, *args):
        processed_args = []
        for arg in args:
            if ( isinstance(arg, basestring) ): processed_args.append("\"" + arg.replace("\"", "\\\"") + "\"")
            elif ( isinstance(arg, list) or isinstance(arg, dict) ): processed_args.append(str(arg))
            else: processed_args.append(str(arg))
        self.js(funcName + "(" + ", ".join(processed_args) + ");")

    def jsFile(self, filename): 
        self.js(self._getFileContents(filename))

    def js(self, data):
        newEntry = HTTPOut.mtEntry()
        newEntry.data = data
        newEntry.js = True
        self.mt_entrys.append(newEntry)
        
    # HTML
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
        self.headers["Date"] = strftime('%a, %d %b %Y %H:%M:%S GMT')
        self.headers["Server"] = "metaTower/0.5"
        content = ""
        socket.settimeout(None)

        if ( self.binary_entry != "" ):
            if ( os.path.isfile(self.binary_entry) ):
                self.status = "200 OK"
                binary_size = os.path.getsize(self.binary_entry)

                if ( self.binary_end == 0 ): self.binary_end = binary_size - 1
                if ( self.binary_start != 0 ) or ( self.binary_end != binary_size - 1 ):
                    self.status = "206 Partial Content"
                    self.headers["Content-Range"] = "bytes " + str(self.binary_start) + "-" + str(self.binary_end) + "/" + str(binary_size)

                self.headers["Accept-Ranges"] = "bytes"
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
                    chunk_size = 1024
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
