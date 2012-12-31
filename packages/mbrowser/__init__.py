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
    mt.events.register("HTTP GET /mbrowser/showcase/", getRawNewest)

    mt.config.load("packages/mbrowser/mbrowser.cfg")
    mt.config.load("packages/mbrowser/viewed.cfg", True)

    scan()

def setupFileRequests():
    global items
    if ( mt.packages.http ):
        http = mt.packages.http
        http.addFile("/mbrowser/images/mtfile.png", "packages/mbrowser/images/mtfile.png")
        http.addFile("/mbrowser/images/mtfolder.png", "packages/mbrowser/images/mtfolder.png")
        http.addFile("/mbrowser/images/icon.png", "packages/mbrowser/images/icon.png")

        for key in items:
            item = items[key]
            mt.events.register("HTTP GET /mbrowser/f/" + item["path"], getFile)
    
def getFile(httpIn, httpOut):
    global items

    path = httpIn.path.replace("/mbrowser/f/", "")

    # generate a list of files from the known library
    found = False
    config_list = mt.config.get("mbrowser/viewed/file")
    for item in config_list:
        if ( item["path"] == path ): found = True
    
    if ( not found ):
        element = mt.config.ConfigItem("")
        element["path"] = path
        mt.config.add(element, "mbrowser/viewed/file", "packages/mbrowser/viewed.cfg")
        mt.config.save("packages/mbrowser/viewed.cfg")
    
    f = items[path]
    if ( f ):
        httpOut.file(path)

def onUnload():
    ffmpeg.stop()

def home(httpOut):
    httpOut.htmlFile("packages/mbrowser/home.html", "container")
    httpOut.jsFile("packages/mbrowser/script.js")
    httpOut.cssFile("packages/mbrowser/style.css")

def getRawIndex(httpIn, httpOut):
    httpOut.headers["Content-Type"] = "text/html"
    httpOut.text("<html><head></head><body>")
    httpOut.text("<a href='#'>Audio - All</a><br>")
    httpOut.text("<a href='#'>Audio - Newest</a><br>")
    httpOut.text("<a href='#'>Video - All</a><br>")
    httpOut.text("<a href='#'>Video - Movies</a><br>")
    httpOut.text("<a href='#'>Video - TV Shows</a><br>")
    httpOut.text("<a href='newest/'>Video - Newest</a><br>")
    httpOut.text("<a href='#'>Refresh Library</a>")
    httpOut.text("</body></html>")

def getRawNewest(httpIn, httpOut):
    lib_results = searchLibrary({'type': 'video'})
    result = {}
    for item in lib_results: result[item["time"]] = item
    sorted_keys = sorted(result)
    
    count = 0    
    output = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
    output += "<html><head><title>Index of /</title></head><body><h1>Index of /</h1>"
    output += '<table><tr><th><img src="/icons/blank.gif" alt="[ICO]"></th><th><a href="?C=N;O=D">Name</a></th><th><a href="?C=M;O=A">Last modified</a></th><th><a href="?C=S;O=A">Size</a></th><th><a href="?C=D;O=A">Description</a></th></tr><tr><th colspan="5"><hr></th></tr>'    
    for key in sorted_keys:
        if ( count >= 50 ): break

        item = result[key]
        base = os.path.basename(item["path"])
        output += '<tr><td valign="top"><img src="/icons/movie.gif" alt="[VID]"></td><td><a href="' + base + '">' + base + '</a></td><td align="right">28-Nov-2012 16:19  </td><td align="right">169M</td><td>&nbsp;</td></tr>'

    output += "</table><address>Apache/2.2.22 (Debian) Server at 192.168.0.5 Port 80</address></body></html>"
    httpOut.headers["Content-Type"] = "text/html;charset=UTF-8"
    httpOut.text(output)    

def getFileList(path):
    results = []
    for f in os.listdir(path):
        ff = os.path.join(path,f)
        if os.path.isdir(ff): results.extend(getFileList(ff))
        if os.path.isfile(ff): results.append(ff)
    return results

def scan():
    global items

    library_path = mt.config["mbrowser/library/path"]
    if ( not os.path.isdir(library_path) ):
        return

    for f in getFileList(mt.config["mbrowser/library/path"]):
        if ( items.has_key(f) ): continue
        idata = processFile(f)
        if ( idata ): items[f] = idata
            
    setupFileRequests()

def processFile(f):
    idata = None
    basename, ext = os.path.splitext(os.path.split(f)[1])
    ext = ext[1:] # drop the .

    video_extensions = mt.config["mbrowser/library/video_extensions"]
    audio_extensions = mt.config["mbrowser/library/audio_extensions"]
    hide_samples = mt.config["mbrowser/library/hide_samples"].isTrue()

    if ( ext in video_extensions ) and ( hide_samples and not "sample" in f.lower() ):
        idata = {}
        idata["id"] = mt.utils.uid()
        idata["path"] = f
        idata["name"] = basename.replace(".", " ").strip()
        idata["type"] = "video"
        idata["time"] = time.time() - os.stat(f).st_mtime
        tv = re.split("(?x)(?i)[\//]*S(\d+)E(\d+)*", idata["name"])
        if ( len(tv) == 4 ):
            idata["tv_name"] = string.capwords(tv[0], " ").strip()
            idata["tv_season"] = tv[1].strip()
            idata["tv_episode"] = tv[2].strip()
            idata["name"] = idata["tv_name"] + " - Season " + idata["tv_season"] + " Episode " + idata["tv_episode"]
            idata["vidtype"] = "tv"
        else:
            idata["vidtype"] = "movie"

            # Process names into a nice "Movie Name (YEAR)" format.
            args = " ".join(basename.split(".")).split(" ")
            name_parts = []
            for arg in args:
                # Test if we've found a valid year.
                year_test = arg.replace("(", "").replace(")", "")
                if ( year_test.isdigit() ):
                    if ( int(year_test) > 1888 and int(year_test) <= this_year and len(name_parts) > 0 ):
                        idata["movie_year"] = year_test
                        break
                name_parts.append(arg)
            idata["name"] = string.capwords(" ".join(name_parts))
            if ( idata.has_key("movie_year") ): idata["name"] += " (" + idata["movie_year"] + ")"

        # check to see if webvideo is available
        webf = f.replace("." + ext, ".flv")
        if ( os.path.isfile(webf) ): idata["web"] = webf

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
    httpOut.js("mbrowser.refreshComplete();")

def tvQuery(httpOut, name = "", season = ""):
    if ( name == "" ):
        parms = {"vidtype": "tv"}
        lib_results = searchLibrary(parms)

        shows = []
        for item in lib_results: shows.append(item["tv_name"])
        shows = mt.utils.removeDuplicates(shows)
        shows.sort()

        httpOut.js("mbrowser.tvShows(" + str(shows) + ");")

    elif ( season == "" ):
        parms = {"vidtype": "tv", "tv_name": name}
        lib_results = searchLibrary(parms)

        seasons = []
        for item in lib_results: seasons.append(item["tv_season"])
        seasons = mt.utils.removeDuplicates(seasons)
        seasons.sort()

        httpOut.js("mbrowser.tvSeasons('" + name + "'," + str(seasons) + ");")

    else:
        parms = {"vidtype": "tv", "tv_name": name, "tv_season": season}
        lib_results = searchLibrary(parms)
        result = {}
        for item in lib_results: result[item["name"]] = item
        
        sorted_keys = sorted(result)
        output = ""
        for key in sorted_keys:
            item = result[key]
            output += ", {'id':'" + item["id"] + "', 'name':'" + item["name"] + "', 'path':'" + item["path"] + "'"
            if ( item.has_key("web") ):
                output += ", 'web': '" + item["web"] + "'"
            if ( item.has_key("external") ):
                output += ", 'external': '" + item["external"] + "'"
            output += "}"
        httpOut.js("mbrowser.tvData('" + name + "', [" + output[2:] + "]);")

def query(httpOut, args, newest = False, limit = 10000, unviewed_only = False):
    lib_results = searchLibrary(args)

    result = {}
    if ( newest ):
        for item in lib_results: result[item["time"]] = item
    else:
        for item in lib_results: result[item["name"]] = item

    flist = []
    if ( unviewed_only ):
        config_list = mt.config.get("mbrowser/viewed/file")
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
    httpOut.js("mbrowser.data([" + output[2:] + "]);")

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
        httpOut.js("mbrowser.externalLink('" + id + "', '" + item["external"] + "');")

def convertStatus(f, prog):
    global converting, convert_success, convert_output
    if ( prog > 100 ):
        setStatus("Finished.", 100)
        converting = False
        convert_output = f
        convert_success = True

        item = findItemById(id)
        if ( item != None ):
            item["web"] = f
    else:
        setStatus("Converting.. (click to stop)", prog)

def convertToWeb(httpOut, id):
    global converting, convert_id, convert_success
    if ( converting ):
        return

    item = findItemById(id)
    if ( item != None ):
        ffmpeg.convertToFlash(item["path"], convertStatus)
        setStatus("Converting.. (click to stop)", 0)
        converting = True
        convert_id = id
        convert_success = False
        status(httpIn, httpOut)

def stopConvert(httpOut):
    global converting
    ffmpeg.stop()
    converting = False
    setStatus("Cancelled.", 100)
    
def setStatus(msg, progress):
    global status_msg, status_prog
    status_msg = msg
    status_prog = progress

def status(httpOut):
    global status_msg, status_prog, convert_success, convert_id, convert_output
    httpOut.js("mbrowser.statusUpdate(\"" + status_msg + "\", " + str(status_prog) + ");")

    if ( status_prog == 100 ) and ( convert_success ):
        httpOut.js("mbrowser.webVideo('" + convert_id + "', '" + convert_output + "');")

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
        httpOut.js("mbrowser.updateFile('" + id + "', " + str(values) + ");")

