import os, re, time, string, mtMisc, ffmpeg
import mtCore as mt

items = {}
status_msg = "Idle."
status_prog = 0
converting = False
convert_id = ""
convert_success = False
convert_output = ""

def onLoad():
    mt.events.register("jman.load", jman_load)
    mt.events.register("jman.menu.mbrowser", jman_menu)

    mt.events.register("jmanlite.load", jmanlite_load)
    mt.events.register("jmanlite.menu.mbrowser", jmanlite_menu)

    scan()

def onUnload():
    ffmpeg.stop()

def jman_load(resp):
    mt.packages.jman.menu(resp.session, "Media Browser", 3)
    mt.packages.jman.taskbar(resp.session, "Media Browser", ['mbrowser_main', 'mbrowser_player'], {"Video Player": "jman.dialog(\"mbrowser_player\");"})
    resp.htmlFile("mbrowser/html/jman.html", "body", True)
    resp.jsFile("mbrowser/js/common.js")
    resp.jsFile("mbrowser/js/jman.js")
    resp.cssFile("mbrowser/css/style.css")

def jman_menu(resp):
    global converting
    scan()
    resp.js("jman.dialog('mbrowser_main');")
    if ( converting ): status(resp)

def jmanlite_load(resp):
    mt.packages.jmanlite.menu(resp.session, "Media Browser", "mbrowser")

def jmanlite_menu(resp):
    scan()
    resp.htmlFile("mbrowser/html/jmanlite.html", "jmanlite_content", False)
    resp.jsFile("mbrowser/js/common.js")
    resp.jsFile("mbrowser/js/jmanlite.js")
    resp.cssFile("mbrowser/css/style.css")

def getFileList(path):
    results = []
    for f in os.listdir(path):
        ff = os.path.join(path,f)
        if os.path.isdir(ff): results.extend(getFileList(ff))
        if os.path.isfile(ff): results.append(ff)
    return results

def scan():
    global items
    for f in getFileList("files/"):
        if ( items.has_key(f) ): continue
        idata = processFile(f)
        if ( idata ): items[f] = idata

def processFile(f):
    idata = None
    basename, ext = os.path.splitext(f)
    if ( ext == ".avi" ) and ( f.lower().find("sample") == -1 ):
        idata = {}
        idata["id"] = mtMisc.uid()
        idata["path"] = f
        idata["name"] = os.path.split(basename)[1].replace(".", " ").strip()
        idata["type"] = "video"
        idata["time"] = time.time() - os.stat(f).st_mtime
        tv = re.split("(?x)(?i)[\//]*S(\d+)E(\d+)*", idata["name"])
        if ( len(tv) == 4 ):
            idata["tv_name"] = string.capwords(tv[0], " ").strip()
            idata["tv_season"] = tv[1].strip()
            idata["tv_episode"] = tv[2].strip()
            idata["name"] = idata["tv_name"] + " - Season " + idata["tv_season"] + " Episode " + idata["tv_episode"]
            idata["vidtype"] = "tv"

        # check to see if webvideo is available
        webf = f.replace(ext, ".flv")
        if ( os.path.isfile(webf) ): idata["web"] = webf

    if ( ext == ".mp3" ):
        idata = {}
        idata["id"] = mtMisc.uid()
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
        shows = mtMisc.removeDuplicates(shows)
        shows.sort()

        resp.js("mbrowser.tvShows(" + str(shows) + ");")

    elif ( season == "" ):
        parms = {"vidtype": "tv", "tv_name": name}
        lib_results = searchLibrary(parms)

        seasons = []
        for item in lib_results: seasons.append(item["tv_season"])
        seasons = mtMisc.removeDuplicates(seasons)
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

def query(resp, ftype = "", newest = False, limit = 10000):
    if ( ftype != "" ): lib_results = searchLibrary({"type": ftype})
    else: lib_results = searchLibrary()

    result = {}
    if ( newest ):
        for item in lib_results: result[item["time"]] = item
    else:
        for item in lib_results: result[item["name"]] = item
    
    #paths = ""
    #names = ""
    count = 0
    sorted_keys = sorted(result)
    output = ""
    for key in sorted_keys:
        if ( count >= limit ): break
        item = result[key]
        output += ", {'id':'" + item["id"] + "', 'name':'" + item["name"] + "', 'path':'" + item["path"] + "'"
        if ( item.has_key("web") ):
            output += ", 'web': '" + item["web"] + "'"
        if ( item.has_key("external") ):
            output += ", 'external': '" + item["external"] + "'"
        output += "}"
        #paths += ", '" + result[key]["path"] + "'"
        #names += ", '" + result[key]["name"] + "'"
        count += 1
    resp.js("mbrowser.data([" + output[2:] + "]);")
    #resp.js("mbrowser.data([" + paths[2:] + "], [" + names[2:] + "]);")

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
        resp.js("mbrowser.externalLink('" + id + "', '*" + item["external"] + "');")

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

