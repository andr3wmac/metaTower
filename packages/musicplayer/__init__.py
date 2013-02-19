import os, re, time, string, ffmpeg, mt

items = {}

status_msg = "Idle."
status_prog = 0
converting = False
convert_id = ""
convert_success = False
convert_output = ""
this_year = int(time.strftime('%Y'))

def onLoad():
    mt.config.load("packages/musicplayer/musicplayer.cfg")
    mt.config.load("packages/musicplayer/viewed.cfg", True)

    scan()

def setupFileRequests():
    global items
    if ( mt.packages.http ):
        http = mt.packages.http
        http.addFile("/musicplayer/images/mtfile.png", "packages/musicplayer/images/mtfile.png")
        http.addFile("/musicplayer/images/mtfolder.png", "packages/musicplayer/images/mtfolder.png")
        http.addFile("/musicplayer/images/icon.png", "packages/musicplayer/images/icon.png")

        for key in items:
            item = items[key]
            mt.events.register("HTTP GET /musicplayer/f/" + item["path"], getFile)
    
def getFile(httpIn, httpOut):
    global items

    path = httpIn.path.replace("/musicplayer/f/", "")

    # generate a list of files from the known library
    found = False
    config_list = mt.config.get("musicplayer/viewed/file")
    for item in config_list:
        if ( item["path"] == path ): found = True
    
    if ( not found ):
        element = mt.config.ConfigItem("")
        element["path"] = path
        mt.config.add(element, "musicplayer/viewed/file", "packages/musicplayer/viewed.cfg")
        mt.config.save("packages/musicplayer/viewed.cfg")
    
    f = items[path]
    if ( f ):
        httpOut.file(path)

def onUnload():
    ffmpeg.stop()

def home(httpOut):
    httpOut.htmlFile("packages/musicplayer/home.html", "container")
    httpOut.jsFile("packages/musicplayer/script.js")
    httpOut.cssFile("packages/musicplayer/style.css")

def getFileList(path):
    results = []
    for f in os.listdir(path):
        ff = os.path.join(path,f)
        if os.path.isdir(ff): results.extend(getFileList(ff))
        if os.path.isfile(ff): results.append(ff)
    return results

def scan():
    global items

    library_path = mt.config["musicplayer/library/path"]
    if ( not os.path.isdir(library_path) ):
        return

    for f in getFileList(mt.config["musicplayer/library/path"]):
        if ( items.has_key(f) ): continue
        idata = processFile(f)
        if ( idata ): items[f] = idata
            
    setupFileRequests()

def processFile(f):
    idata = None
    basename, ext = os.path.splitext(os.path.split(f)[1])
    ext = ext[1:] # drop the .

    audio_extensions = mt.config["musicplayer/library/audio_extensions"]

    if ( ext in audio_extensions ):
        idata = {}
        idata["id"] = mt.utils.uid()
        idata["path"] = f
        idata["name"] = os.path.split(basename)[1]
        idata["type"] = "audio"
        idata["time"] = time.time() - os.stat(f).st_mtime
        
    return idata
            
def refresh():
    global items
    items = {}
    scan()

def refreshLibrary(httpOut):
    refresh()
    httpOut.js("musicplayer.refreshComplete();")

def query(httpOut, args, newest = False, limit = 10000, unviewed_only = False):
    lib_results = searchLibrary(args)

    result = {}
    if ( newest ):
        for item in lib_results: result[item["time"]] = item
    else:
        for item in lib_results: result[item["name"]] = item

    flist = []
    if ( unviewed_only ):
        config_list = mt.config.get("musicplayer/viewed/file")
        for item in config_list:
            flist.append(item["path"])
    
    #paths = ""
    #names = ""
    count = 0
    sorted_keys = sorted(result)
    output = ""
    for key in sorted_keys:
        if ( count >= limit ): break
        item = result[key]

        if ( unviewed_only ):
            if ( item["path"] in flist ): continue
        
        output += ", {'id':'" + item["id"] + "', 'name':'" + item["name"].replace("'", "\\'") + "', 'path':'" + item["path"].replace("'", "\\'") + "'"

        # check if it has a weblink.
        if ( item.has_key("web") ):
            output += ", 'web': '" + item["web"] + "'"

        # check for external link.
        if ( item.has_key("external") ):
            output += ", 'external': '" + item["external"] + "'"
        output += "}"
        count += 1
    httpOut.js("musicplayer.data([" + output[2:] + "]);")

def searchLibrary(parms):
    results = []
    for key in items:
        item = items[key]
        satisfied_parms = 0
        for pkey in parms:
            if ( item.has_key(pkey) ) and ( item[pkey] == parms[pkey] ): satisfied_parms += 1
        if ( satisfied_parms == len(parms) ): results.append(item)
    return results

def findItemById(id):
    global items
    for key in items:
        i = items[key]
        if ( i.has_key("id") ) and ( i["id"] == id ): return i
    return None
        
def getExternalLink(httpOut, id):
    item = findItemById(id)
    if ( item != None ):
        item["external"] = httpOut.session.generateFileKey(item["path"])
        httpOut.js("musicplayer.externalLink('" + id + "', '" + item["external"] + "');")
    
def setStatus(msg, progress):
    global status_msg, status_prog
    status_msg = msg
    status_prog = progress

def status(httpOut):
    global status_msg, status_prog, convert_success, convert_id, convert_output
    httpOut.js("musicplayer.statusUpdate(\"" + status_msg + "\", " + str(status_prog) + ");")

    if ( status_prog == 100 ) and ( convert_success ):
        httpOut.js("musicplayer.webVideo('" + convert_id + "', '" + convert_output + "');")

def rename(httpOut, id, new):
    global items
    item = findItemById(id)
    if ( item ):
        old = item["path"]
        old_dir = os.path.dirname(old)
        new = os.path.join(old_dir, new)
        os.rename(old, new)

        if ( item.has_key("web") ):
            basename, ext = os.path.splitext(old)
            os.rename(item["web"], new.replace(ext, ".flv"))
        
        new_item = processFile(new)
        new_item["id"] = id

        items[new] = new_item
        del items[old]

        values = {'name': new_item["name"], 'path': new_item["path"]}
        if ( new_item.has_key("web") ): values["web"] = new_item["web"]
        httpOut.js("musicplayer.updateFile('" + id + "', " + str(values) + ");")

