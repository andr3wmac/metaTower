import mt, socket
from HTTPServer import HTTPServer

def onLoad():
    mt.events.register("HTTP GET /", getIndex)

    # load config file and users.
    mt.config.load("packages/http/http.cfg")
    user_list = mt.config.get("http/users/user")
    for user in user_list:
        addUser(user["username"], user["password"])

    if ( start() ):
        mt.log.info("Started on port " + mt.config["http/port"])
    else:
        mt.log.error("Could not start on port " + mt.config["http/port"])

# Users
users = {}
class User:
    def __init__(self, name, password, key = ""):
        self.name = name
        self.password = password
        self.key = key

def addUser(name, password, key = ""):
    global users
    users[name] = User(name, password, key)

def getUser(name):
    global users
    if users.has_key(name): return users[name]
    return None

# Scripts to be loaded on index.
scripts = ["metaTower.js"]
def addScript(path):
    global scripts
    if ( not path in scripts ): scripts.append(path)    

def addScripts(scriptlist):
    for s in scriptlist: addScript(s)

# Stylesheets.
styles = []
def addStyle(path):
    global styles
    if ( not path in styles ): styles.append(path)

def addStyles(stylelist):
    for s in stylelist: addStyle(s)

# File Requests
files = {}
def addFile(request, filepath):
    global files
    files[request] = filepath
    mt.events.register("HTTP GET " + request, getFile)
    mt.events.register("HTTP HEAD " + request, getFile)
def addFiles(filelist):
    for f in filelist: addFile(f, filelist[f])

def getFile(httpIn, httpOut):
    global files
    if ( files.has_key(httpIn.path) ):    
        httpOut.file(files[httpIn.path])    

# Empty shell html, to be filled by a window manager.
def getIndex(httpIn, httpOut):
    global scripts, styles

    httpOut.headers["Content-Type"] = "text/html"
    httpOut.text("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\" \"http://www.w3.org/TR/html4/strict.dtd\">\n")
    httpOut.text("<html>\n")
    httpOut.text("<head>\n")
    httpOut.text("<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />")
    httpOut.text("<title>metaTower</title>")

    for style in styles:
        httpOut.text("<link href=\"" + style + "\" rel=\"stylesheet\" type=\"text/css\" />\n")

    for script in scripts:
        httpOut.text("<script type=\"text/javascript\" src=\"" + script + "\"></script>")

    httpOut.text("</head>")
    httpOut.text("<body onLoad=\"mt.load();\"></body>")
    httpOut.text("</html>")

# Runs the HTTP server.
def start():
    global http_thread
    try:
        addr = ("", int(mt.config["http/port"]))
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
