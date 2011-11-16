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
    
def remove_selected(session, selected):
    global QueueControl

    items = selected.split(",")
    QueueControl.removeItems(items)
    return update(session)

def jman_load(session):
    packages.jman.menu(session, "Download Manager", 0)
    packages.jman.taskbar(session, "Download Manager", ['dlmanager_main'])
    out = session.out()
    out.htmlFile("dlmanager/html/jman.html", "body", True)
    out.jsFile("dlmanager/js/common.js")
    out.jsFile("dlmanager/js/jman.js")
    out.cssFile("dlmanager/css/style.css")
    return out
    
def jman_menu(session):
    out = session.out()
    out.js("jman.dialog('dlmanager_main');")
    out.append(update(session))
    return out

def jmanlite_load(session):
    packages.jmanlite.menu(session, "Download Manager", "dlmanager")
    return None
    
def jmanlite_menu(session):
    out = session.out()
    out.htmlFile("dlmanager/html/jmanlite.html", "jmanlite_content", False)
    out.jsFile("dlmanager/js/common.js")
    out.jsFile("dlmanager/js/jmanlite.js")
    out.cssFile("dlmanager/css/style.css")
    out.append(update(session))
    return out

def update(session):
    global QueueControl
    nzb_engine = QueueControl.nzb_engine
    nzb_queue = QueueControl.nzb_queue
    torrent_engine = QueueControl.torrent_engine
    torrent_queue = QueueControl.torrent_queue

    # prepare our session.
    out = session.out()

    # list of nzbs.
    for nzb in nzb_queue:
        if ( nzb.removed ):
            out.js("dlmanager.remove('" + nzb.uid + "');")
        elif ( nzb.downloading ) and ( nzb_engine != None ) and ( nzb_engine.running ):
            status = nzb_engine.status

            out.js("dlmanager.nzb('" + nzb.uid + "', '" + os.path.basename(nzb.filename) + "', 1, " + str(status.total_bytes/1048576) + "," + str(status.current_bytes/1048576) + "," + str(round(status.current_bytes/float(status.total_bytes)*100)) + "," + str(status.kbps) + ");")
        elif ( nzb.completed ):
            # completed
            out.js("dlmanager.nzb('" + nzb.uid + "', '" + os.path.basename(nzb.filename) + "', 2, 0, 0, 0, 0, '" + nzb.par2_results + "', '" + nzb.unrar_results + "');")
        elif ( nzb.error ):
            # failed
            out.js("dlmanager.nzb('" + nzb.uid + "', '" + os.path.basename(nzb.filename) + "', 3);")
        else:
            # queued
            out.js("dlmanager.nzb('" + nzb.uid + "', '" + os.path.basename(nzb.filename) + "', 0);")

    for torrent in torrent_queue:
        if ( torrent.removed ):
            out.js("dlmanager.remove('" + torrent.uid + "');")
        elif ( torrent.lt_entry == None ):
            out.js("dlmanager.torrent('" + torrent.uid + "', '" + os.path.basename(torrent.filename) + "', 0);")
        else:
            status = torrent.lt_entry.status()
            out.js("dlmanager.torrent('" + torrent.uid + "', '" + os.path.basename(torrent.filename) + "', 1, " + str(status.progress * 100) + ", '" + str(round(status.download_rate / 1000, 2)) + " kb/s');")

    out.js("dlmanager.update();")
    return out

