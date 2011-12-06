import os, threading, commands, mtMisc, time
import mtCore as mt
from mtCore import config
from mtCore import events
from mtCore import packages
from xml.etree.ElementTree import Element
from QueueController import QueueController

QueueControl = None
last_update = 0

def onLoad():
    global QueueControl

    # load configuration
    config.load("packages/dlmanager/dlmanager.xml")
    
    # start up our queue monitor.
    QueueControl = QueueController()
    QueueControl.start()
    
    # register events.
    events.register("jman.load", jman_load)
    events.register("jman.menu.dlmanager", jman_menu)
    events.register("jmanlite.load", jmanlite_load)
    events.register("jmanlite.menu.dlmanager", jmanlite_menu)
    
def onUnload():
    global QueueControl

    if ( QueueControl != None ):
        torrent_queue = QueueControl.torrent_queue
        nzb_queue = QueueControl.nzb_queue

        config = mt.config
        config.clear("dlmanager/queue")

        for item in nzb_queue:
            if ( item.removed ): continue
            element = config.ConfigItem("")
            element["uid"] = item.uid
            element["filename"] = item.filename
            element["completed"] = str(int(item.completed))
            element["error"] = str(int(item.error))
            element["par2_results"] = item.par2_results
            element["unrar_results"] = item.unrar_results
            element["save_to"] = item.save_to
            config.add(element, "dlmanager/queue/nzb", "packages/dlmanager/dlmanager.xml")

        for item in torrent_queue:
            if ( item.removed ): continue
            element = config.ConfigItem("")
            element["uid"] = item.uid
            element["filename"] = item.filename
            element["completed"] = str(int(item.completed))
            element["error"] = str(int(item.error))
            element["save_to"] = item.save_to
            config.add(element, "dlmanager/queue/torrent", "packages/dlmanager/dlmanager.xml")

        config.save("packages/dlmanager/dlmanager.xml")
        QueueControl.shutdown()
    
def remove_selected(resp, selected):
    global QueueControl

    items = selected.split(",")
    QueueControl.removeItems(items)
    update(session, resp)

def jman_load(resp):
    packages.jman.menu(resp.session, "Download Manager", 0)
    packages.jman.taskbar(resp.session, "Download Manager", ['dlmanager_main'])
    resp.htmlFile("dlmanager/html/jman.html", "body", True)
    resp.jsFile("dlmanager/js/common.js")
    resp.jsFile("dlmanager/js/jman.js")
    resp.cssFile("dlmanager/css/style.css")
    
def jman_menu(resp):
    resp.js("jman.dialog('dlmanager_main');")
    update(resp)

def jmanlite_load(resp):
    packages.jmanlite.menu(resp.session, "Download Manager", "dlmanager")
    
def jmanlite_menu(resp):
    resp.htmlFile("dlmanager/html/jmanlite.html", "jmanlite_content", False)
    resp.jsFile("dlmanager/js/common.js")
    resp.jsFile("dlmanager/js/jmanlite.js")
    resp.cssFile("dlmanager/css/style.css")
    update(session, resp)

def update(resp):
    global QueueControl
    nzb_engine = QueueControl.nzb_engine
    nzb_queue = QueueControl.nzb_queue
    torrent_engine = QueueControl.torrent_engine
    torrent_queue = QueueControl.torrent_queue

    # list of nzbs.
    for nzb in nzb_queue:
        if ( nzb.removed ):
            resp.js("dlmanager.remove('" + nzb.uid + "');")
        elif ( nzb.downloading ) and ( nzb_engine != None ) and ( nzb_engine.running ):
            status = nzb_engine.status
            filename = os.path.basename(nzb.filename).replace("'", "\'")

            resp.js("dlmanager.nzb('" + nzb.uid + "', '" + filename + "', 1, " + str(status.total_bytes/1048576) + "," + str(status.current_bytes/1048576) + "," + str(round(status.current_bytes/float(status.total_bytes)*100)) + "," + str(status.kbps) + ");")
        elif ( nzb.completed ):
            # completed
            filename = os.path.basename(nzb.filename).replace("'", "\'")
            resp.js("dlmanager.nzb('" + nzb.uid + "', '" + filename + "', 2, 0, 0, 0, 0, '" + nzb.par2_results + "', '" + nzb.unrar_results + "');")
        elif ( nzb.error ):
            # failed
            filename = os.path.basename(nzb.filename).replace("'", "\'")
            resp.js("dlmanager.nzb('" + nzb.uid + "', '" + filename + "', 3);")
        else:
            # queued
            filename = os.path.basename(nzb.filename).replace("'", "\'")
            resp.js("dlmanager.nzb('" + nzb.uid + "', '" + filename + "', 0);")

    for torrent in torrent_queue:
        if ( torrent.removed ):
            resp.js("dlmanager.remove('" + torrent.uid + "');")
        elif ( torrent.lt_entry == None ):
            resp.js("dlmanager.torrent('" + torrent.uid + "', '" + os.path.basename(torrent.filename) + "', 0);")
        else:
            status = torrent.lt_entry.status()
            resp.js("dlmanager.torrent('" + torrent.uid + "', '" + os.path.basename(torrent.filename) + "', 1, " + str(status.progress * 100) + ", '" + str(round(status.download_rate / 1000, 2)) + " kb/s');")

    resp.js("dlmanager.update();")

