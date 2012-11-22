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
    #mt.requests.addFunction("GET", "/mbrowser/f/", getRawIndex)
    #mt.requests.addFunction("GET", "/mbrowser/f/newest/", getRawNewest)

    mt.config.load("packages/mbrowser/mbrowser.cfg")
    mt.config.load("packages/mbrowser/viewed.cfg", True)

    scan()

def setupFileRequests():
    mt.requests.clearFileRequests()

    global items

    mt.requests.addFile("GET", "/mbrowser/images/mtfile.png", "packages/mbrowser/images/mtfile.png")
    mt.requests.addFile("GET", "/mbrowser/images/mtfolder.png", "packages/mbrowser/images/mtfolder.png")

    for key in items:
        item = items[key]
        mt.requests.addFunction("GET", "/mbrowser/f/" + item["path"], getFile)
        #mt.requests.addFile("GET", "/mbrowser/f/" + item["path"], item["path"])
    
def getFile(resp, httpIn):
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
        resp.file(path)

def onUnload():
    mt.requests.clearFileRequests()
    ffmpeg.stop()

def home(resp):
    resp.htmlFile("packages/mbrowser/home.html", "container")
    resp.jsFile("packages/mbrowser/script.js")
    resp.cssFile("packages/mbrowser/style.css")

def getRawIndex(resp):
    resp.headers["Content-Type"] = "text/html"
    resp.text("<a href='#'>Audio - All</a><br>")
    resp.text("<a href='#'>Audio - Newest</a><br>")
    resp.text("<a href='#'>Video - All</a><br>")
    resp.text("<a href='#'>Video - Movies</a><br>")
    resp.text("<a href='#'>Video - TV Shows</a><br>")
    resp.text("<a href='newest/'>Video - Newest</a><br>")
    resp.text("<a href='#'>Refresh Library</a>")

def getRawNewest(resp):
    lib_results = searchLibrary({'type': 'video'})
    result = {}
    for item in lib_results: result[item["time"]] = item
    sorted_keys = sorted(result)
    
    count = 0    
    output = "<a href='The Julianne Show S01E03.avi'>The Julianne Show S01E03.avi</a>"
    for key in sorted_keys:
        if ( count >= 50 ): break

        item = result[key]
        output += "<a href='" + item["path"] + "'>" + item["name"] + "</a><br>"

    resp.headers["Content-Type"] = "text/html"
    resp.text(output)    

def getFileList(path):
    results = []
    for f in os.listdir(path):
        ff = os.path.join(path,f)
        if os.path.isdir(ff): results.extend(getFileList(ff))
        if os.path.isfile(ff): results.append(ff)
    return results

def scan():
    global items

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

def refreshLibrary(resp):
    refresh()
    resp.js("mbrowser.refreshComplete();")

def tvQuery(resp, name = "", season = ""):
    if ( name == "" ):
        parms = {"vidtype": "tv"}
        lib_results = searchLibrary(parms)

        shows = []
        for item in lib_results: shows.append(item["tv_name"])
        shows = mt.utils.removeDuplicates(shows)
        shows.sort()

        resp.js("mbrowser.tvShows(" + str(shows) + ");")

    elif ( season == "" ):
        parms = {"vidtype": "tv", "tv_name": name}
        lib_results = searchLibrary(parms)

        seasons = []
        for item in lib_results: seasons.append(item["tv_season"])
        seasons = mt.utils.removeDuplicates(seasons)
        seasons.sort()

        resp.js("mbrowser.tvSeasons('" + name + "'," + str(seasons) + ");")

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
        resp.js("mbrowser.tvData('" + name + "', [" + output[2:] + "]);")

def query(resp, args, newest = False, limit = 10000, unviewed_only = False):
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
        
        output += ", {'id':'" + item["id"] + "', 'name':'" + item["name"] + "', 'path':'" + item["path"] + "'"

        # check if it has a weblink.
        if ( item.has_key("web") ):
            output += ", 'web': '" + item["web"] + "'"

        # check for external link.
        if ( item.has_key("external") ):
            output += ", 'external': '" + item["external"] + "'"
        output += "}"
        count += 1
    resp.js("mbrowser.data([" + output[2:] + "]);")

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
        
def getExternalLink(resp, id):
    item = findItemById(id)
    if ( item != None ):
        item["external"] = resp.session.generateFileKey(item["path"])
        resp.js("mbrowser.externalLink('" + id + "', '" + item["external"] + "');")

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

def convertToWeb(resp, id):
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
        status(resp)

def stopConvert(resp):
    global converting
    ffmpeg.stop()
    converting = False
    setStatus("Cancelled.", 100)
    
def setStatus(msg, progress):
    global status_msg, status_prog
    status_msg = msg
    status_prog = progress

def status(resp):
    global status_msg, status_prog, convert_success, convert_id, convert_output
    resp.js("mbrowser.statusUpdate(\"" + status_msg + "\", " + str(status_prog) + ");")

    if ( status_prog == 100 ) and ( convert_success ):
        resp.js("mbrowser.webVideo('" + convert_id + "', '" + convert_output + "');")

def rename(resp, id, new):
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
        resp.js("mbrowser.updateFile('" + id + "', " + str(values) + ");")

