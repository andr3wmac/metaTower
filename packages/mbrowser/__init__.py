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

def jman_load(session):
    mt.packages.jman.menu(session, "Media Browser", 3)
    mt.packages.jman.taskbar(session, "Media Browser", ['mbrowser_main', 'mbrowser_player'], {"Video Player": "jman.dialog(\"mbrowser_player\");"})
    out = session.out()
    out.htmlFile("mbrowser/html/jman.html", "body", True)
    out.jsFile("mbrowser/js/common.js")
    out.jsFile("mbrowser/js/jman.js")
    out.cssFile("mbrowser/css/style.css")
    return out

def jman_menu(session):
    global converting
    scan()
    out = session.out()
    out.js("jman.dialog('mbrowser_main');")
    if ( converting ): out.append(status(session))
    return out

def jmanlite_load(session):
    mt.packages.jmanlite.menu(session, "Media Browser", "mbrowser")
    return None

def jmanlite_menu(session):
    scan()
    out = session.out()
    out.htmlFile("mbrowser/html/jmanlite.html", "jmanlite_content", False)
    out.jsFile("mbrowser/js/common.js")
    out.jsFile("mbrowser/js/jmanlite.js")
    out.cssFile("mbrowser/css/style.css")
    return out

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
        basename, ext = os.path.splitext(f)
        if ( items.has_key(f) ): continue
        if ( ext == ".avi" ) and ( f.lower().find("sample") == -1 ):
            idata = {}
            idata["id"] = mtMisc.uid()
            idata["path"] = f
            idata["name"] = os.path.split(basename)[1].replace(".", " ").strip()
            idata["type"] = "video"
            idata["time"] = time.time() - os.stat(f).st_mtime
            tv = re.split("(?x)(?i)[\//]*S(\d+)E(\d+)*", idata["name"])
            if ( len(tv) == 4 ):
                idata["tv_name"] = string.capwords(tv[0], " ")
                idata["tv_season"] = tv[1]
                idata["tv_episode"] = tv[2]
                idata["name"] = idata["tv_name"] + " - Season " + idata["tv_season"] + " Episode " + idata["tv_episode"]
                idata["vidtype"] = "tv"

            # check to see if webvideo is available
            webf = f.replace(ext, ".flv")
            if ( os.path.isfile(webf) ): idata["web"] = webf

            items[f] = idata

        if ( ext == ".mp3" ):
            idata = {}
            idata["id"] = mtMisc.uid()
            idata["path"] = f
            idata["name"] = os.path.split(basename)[1]
            idata["type"] = "audio"
            idata["time"] = time.time() - os.stat(f).st_mtime
            items[f] = idata
            
def refresh():
    global items
    items = {}
    scan()

def refreshLibrary(session):
    out = session.out()
    refresh()
    out.js("mbrowser.refreshComplete();")
    return out

def tvQuery(session, name = "", season = ""):
    out = session.out()

    if ( name == "" ):
        parms = {"vidtype": "tv"}
        lib_results = searchLibrary(parms)

        shows = []
        for item in lib_results: shows.append(item["tv_name"])
        shows = mtMisc.removeDuplicates(shows)
        shows.sort()

        out.js("mbrowser.tvShows(" + str(shows) + ");")

    elif ( season == "" ):
        parms = {"vidtype": "tv", "tv_name": name}
        lib_results = searchLibrary(parms)

        seasons = []
        for item in lib_results: seasons.append(item["tv_season"])
        seasons = mtMisc.removeDuplicates(seasons)
        seasons.sort()

        out.js("mbrowser.tvSeasons('" + name + "'," + str(seasons) + ");")

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
        out.js("mbrowser.tvData('" + name + "', [" + output[2:] + "]);")

    return out

def query(session, ftype = "", newest = False, limit = 10000):
    out = session.out()

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
    out.js("mbrowser.data([" + output[2:] + "]);")
    #out.js("mbrowser.data([" + paths[2:] + "], [" + names[2:] + "]);")
    return out

def searchLibrary(parms):
    results = []
    for key in items:
        item = items[key]
        satisfied = False
        if ( len(parms) == 0 ): satisfied = True
        for pkey in parms:
            if ( item.has_key(pkey) ) and ( item[pkey] == parms[pkey] ): satisfied = True
            else: satisfied = False
        if ( satisfied ): results.append(item)
    return results

def findItemById(id):
    global items
    for key in items:
        i = items[key]
        if ( i["id"] == id ): return i
    return None
        
def getExternalLink(session, id):
    out = session.out()
    
    item = findItemById(id)
    if ( item != None ):
        item["external"] = session.generateFileKey(item["path"])
        out.js("mbrowser.externalLink('" + id + "', '*" + item["external"] + "');")
    return out

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

def convertToWeb(session, id):
    global converting, convert_id, convert_success
    if ( converting ):
        return

    out = session.out()
    item = findItemById(id)
    if ( item != None ):
        ffmpeg.convertToFlash(item["path"], convertStatus)
        setStatus("Converting.. (click to stop)", 0)
        converting = True
        convert_id = id
        convert_success = False
        out.append(status(session))
    return out

def stopConvert(session):
    global converting
    ffmpeg.stop()
    converting = False
    setStatus("Cancelled.", 100)
    
def setStatus(msg, progress):
    global status_msg, status_prog
    status_msg = msg
    status_prog = progress

def status(session):
    global status_msg, status_prog, convert_success, convert_id, convert_output
    out = session.out()
    out.js("mbrowser.statusUpdate(\"" + status_msg + "\", " + str(status_prog) + ");")

    if ( status_prog == 100 ) and ( convert_success ):
        out.js("mbrowser.webVideo('" + convert_id + "', '" + convert_output + "');")

    return out

