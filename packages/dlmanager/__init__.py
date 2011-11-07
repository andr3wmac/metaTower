import os, threading, commands, mtMisc, time
import mtCore as mt
from mtCore import events
from mtCore import packages
from xml.etree.ElementTree import Element
from QueueController import QueueController

QueueControl = None
last_update = 0

def onLoad():
    global QueueControl

    # directory fix.
    if ( not os.path.isdir("packages/dlmanager/queue") ): os.mkdir("packages/dlmanager/queue")
    if ( not os.path.isdir("packages/dlmanager/cache") ): os.mkdir("packages/dlmanager/cache")

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
        QueueControl.shutdown()
    
def remove_selected(session, selected):
    global QueueControl

    items = selected.split(",")
    QueueControl.removeItems(items)
    return update(session)

def jman_load(session):
    packages.jman.menu(session, "Download Manager", {"package": "dlmanager", "dialogs": ['dlmanager_main']})
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

    # list of torrents.
    for torrent in torrent_queue:
        if ( torrent.removed ):
            out.js("dlmanager.remove('" + torrent.uid + "');")

        state = 0
        if ( torrent.completed ):
            state = 2

        filename = os.path.basename(torrent.filename)
        if ( torrent.realFilename != None ):
            filename = torrent.realFilename

        if ( torrent_engine != None ):
            if ( torrent.filename == torrent_engine.filename ):
                if ( torrent_engine.realFilename != None ): filename = torrent_engine.realFilename
                out.js("dlmanager.torrent('" + torrent.uid + "', '" + filename + "', 1, " + str(torrent_engine.percentDone) + ", '" + torrent_engine.downRate + "');")
            else:
                out.js("dlmanager.torrent('" + torrent.uid + "', '" + filename + "', " + str(state) + ");")
        else:
            out.js("dlmanager.torrent('" + torrent.uid + "', '" + filename + "', " + str(state) + ");")
            

    out.js("dlmanager.update();")
    return out

