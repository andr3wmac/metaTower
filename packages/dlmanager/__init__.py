import os, threading, commands, mt, time
from xml.etree.ElementTree import Element
from QueueController import QueueController

QueueControl = None
last_update = 0

def onLoad():
    global QueueControl

    # load configuration
    mt.config.load("packages/dlmanager/dlmanager.cfg")
    
    # start up our queue monitor.
    QueueControl = QueueController()
    QueueControl.start()

    # register http requests
    mt.requests.addFunction("POST", "/packages/dlmanager/queue/", onUpload)
    mt.requests.addFile("GET", "/dlmanager/images/nzb.png", "dlmanager/images/nzb.png")
    mt.requests.addFile("GET", "/dlmanager/images/par2.png", "dlmanager/images/par2.png")
    mt.requests.addFile("GET", "/dlmanager/images/torrent.png", "dlmanager/images/torrent.png")
    mt.requests.addFile("GET", "/dlmanager/images/unrar.png", "dlmanager/images/unrar.png")    

def onUnload():
    global QueueControl

    if ( QueueControl != None ):
        torrent_queue = QueueControl.torrent_queue
        nzb_queue = QueueControl.nzb_queue

        mt.config.clear("dlmanager/queue")
        for item in nzb_queue:
            if ( item.removed ): continue
            element = mt.config.ConfigItem("")
            element["uid"] = item.uid
            element["filename"] = item.filename
            element["completed"] = str(int(item.completed))
            element["error"] = str(int(item.error))
            element["par2_results"] = item.par2_results
            element["unrar_results"] = item.unrar_results
            element["save_to"] = item.save_to
            mt.config.add(element, "dlmanager/queue/nzb", "packages/dlmanager/dlmanager.cfg")

        for item in torrent_queue:
            if ( item.removed ): continue
            element = mt.config.ConfigItem("")
            element["uid"] = item.uid
            element["filename"] = item.filename
            element["completed"] = str(int(item.completed))
            element["error"] = str(int(item.error))
            element["save_to"] = item.save_to
            mt.config.add(element, "dlmanager/queue/torrent", "packages/dlmanager/dlmanager.cfg")

        mt.config.save("packages/dlmanager/dlmanager.cfg")
        QueueControl.stop()
    
def onUpload(resp, httpIn):
    post_args = httpIn.post_data.splitlines()
        
    content_type = ""
    form_name = ""
    file_name = ""
    file_data = ""
    
    x = 1
    while x < len(post_args):
        line = post_args[x]
        if ( line[0:20] == "Content-Disposition:" ):
            args = line.split('"')
            form_name = args[1]
            file_name = args[3]
        if ( line[0:14] == "Content-Type: " ):
            content_type = line
        if (( file_name != "" ) and ( line == "" )):
            file_data = httpIn.post_data.split(content_type + "\r\n\r\n")[1]
            file_data = file_data[0:len(file_data)-4]
            break
            
        x += 1
            
    if (( file_name != "" ) and ( file_data != "" )):
        f = open(os.path.join("packages/dlmanager/queue/", file_name), "wb")
        f.write(file_data)
        f.close()
        output.text("Upload successful.")

def remove_selected(resp, selected):
    global QueueControl

    items = selected.split(",")
    QueueControl.removeItems(items)
    update(resp)

def home(resp):
    resp.htmlFile("dlmanager/home.html", "container")
    resp.jsFile("dlmanager/script.js")
    resp.cssFile("dlmanager/style.css")

def update(resp):
    global QueueControl
    nzb_engine = QueueControl.nzb_engine
    nzb_queue = QueueControl.nzb_queue
    torrent_engine = QueueControl.torrent_engine
    torrent_queue = QueueControl.torrent_queue

    # gather data from NZB queue.
    for nzb in nzb_queue:
        # already deleted.
        if ( nzb.removed ):
            resp.js("dlmanager.remove('" + nzb.uid + "');")

        # downloading
        elif ( nzb.downloading ) and ( nzb_engine != None ) and ( nzb_engine.running ):
            status = nzb_engine.execute("getStatus")
            filename = os.path.basename(nzb.filename).replace("'", "\'")

            # State 1: currently downloading
            if ( not status.assembly ):
                args = {"total": int(status.total_bytes/1048576), 
                        "completed": int(status.current_bytes/1048576),
                        "percent": round(status.current_bytes/float(status.total_bytes)*100),
                        "dl_rate": status.kbps}
                resp.js("dlmanager.nzb('" + nzb.uid + "', '" + filename + "', 1, " + str(args) + ");")

            # State 2: being assembled.
            else:
                args = {"assembly_percent": status.assembly_percent}
                resp.js("dlmanager.nzb('" + nzb.uid + "', '" + filename + "', 2, " + str(args) + ");")

        # State 3: failed
        elif ( nzb.error ):
            filename = os.path.basename(nzb.filename).replace("'", "\'")
            resp.js("dlmanager.nzb('" + nzb.uid + "', '" + filename + "', 3);")

        # State 4: completed
        elif ( nzb.completed ):
            filename = os.path.basename(nzb.filename).replace("'", "\'")
            args = {"par2": nzb.par2_results, 
                    "unrar": nzb.unrar_results}
            resp.js("dlmanager.nzb('" + nzb.uid + "', '" + filename + "', 4, " + str(args) + ");")

        # State 0: queued
        else:
            filename = os.path.basename(nzb.filename).replace("'", "\'")
            resp.js("dlmanager.nzb('" + nzb.uid + "', '" + filename + "', 0);")

    # Gather data from torrent queue.
    for torrent in torrent_queue:
        # Torrent Removed.
        if ( torrent.removed ):
            resp.js("dlmanager.remove('" + torrent.uid + "');")

        # Torrent is inactive.
        elif ( torrent.lt_entry == None ):
            resp.js("dlmanager.torrent('" + torrent.uid + "', '" + os.path.basename(torrent.filename) + "', 0);")

        # Torrent is in an active state.
        else:
            status = torrent.lt_entry.status()
            state_str = ['Queued.', 'Checking..', 'Downloading metadata..', 'Downloading..', 'Finished.', 'Seeding.', 'Allocating..']
            args = {"msg": state_str[status.state],
                    "progress": status.progress * 100,
                    "dl_rate": round(status.download_rate / 1000, 2),
                    "ul_rate": round(status.upload_rate / 1000, 2),
                    "peers": status.num_peers}
            resp.js("dlmanager.torrent('" + torrent.uid + "', '" + os.path.basename(torrent.filename) + "', 1, " + str(args) + ");")

    # Trigger an update for next time.
    resp.js("dlmanager.update();")

