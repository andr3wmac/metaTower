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
    
    # register events.
    mt.events.register("jman.load", jman_load)
    mt.events.register("jman.menu.dlmanager", jman_menu)
    mt.events.register("mtwm.load", mtwm_load)
    mt.events.register("mtwm.menu.dlmanager", mtwm_menu)
    
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
    
def remove_selected(resp, selected):
    global QueueControl

    items = selected.split(",")
    QueueControl.removeItems(items)
    update(resp)

def jman_load(resp):
    mt.packages.jman.menu(resp.session, "Download Manager", 0)
    mt.packages.jman.taskbar(resp.session, "Download Manager", ['dlmanager_main'])
    resp.htmlFile("dlmanager/html/jman.html", "body", True)
    resp.jsFile("dlmanager/js/common.js")
    resp.jsFile("dlmanager/js/jman.js")
    resp.cssFile("dlmanager/css/style.css")
    
def jman_menu(resp):
    resp.js("jman.dialog('dlmanager_main');")
    update(resp)

def mtwm_load(resp):
    mt.packages.mtwm.menu(resp.session, "Download Manager", "dlmanager")
    
def mtwm_menu(resp):
    resp.htmlFile("dlmanager/html/mtwm.html", "mtwm_content", False)
    resp.jsFile("dlmanager/js/common.js")
    resp.jsFile("dlmanager/js/mtwm.js")
    resp.cssFile("dlmanager/css/style.css")
    update(resp)

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

