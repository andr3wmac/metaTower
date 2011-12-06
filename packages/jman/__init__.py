import time
import mtCore as mt
import mtMisc as misc

def onLoad():
    mt.events.register("jman.onIndex", onIndex)
    mt.events.register("jman.onPageLoad", onPageLoad)

def onUnload():
    mt.events.clear(onIndex)
    mt.events.clear(onPageLoad)

def onIndex(resp):
    resp.session.jman_menu = []
    resp.session.jman_taskbar = []
    resp.file("jman/index.html")
    
def onPageLoad(resp):
    mt.events.trigger("jman.load", resp)

    # sort menu data by priority
    resp.session.jman_menu = sorted(resp.session.jman_menu, key=lambda e: e.priority) 
    
    # dump menu data
    menuJS = ""
    for entry in resp.session.jman_menu:
        menuJS += "jman.menu.add('" + entry.package_name  + "', '" + entry.caption + "', " + str(entry.priority) + ", '" + entry.onClick + "');"
    resp.js(menuJS)

    # dump package data
    packageJS = ""
    for entry in resp.session.jman_taskbar:
        packageJS += "jman.taskbar.add('" + entry.package_name + "', '" + entry.caption + "', " + str(entry.dialogs) + ", " + str(entry.context_menu) + ");"
    resp.js(packageJS)

    resp.js("jman.finishedLoading();")

class TaskbarEntry:
    package_name = ""
    caption = ""
    dialogs = []
    context_menu = {}

class MenuEntry:
    package_name = ""
    caption = ""
    priority = 5
    onClick = ""

def menu(session, caption, priority = 0, onClick = ""):
    entry = MenuEntry()
    entry.package_name = misc.getSource()
    entry.caption = caption
    entry.priority = priority
    entry.onClick = onClick    
    session.jman_menu.append(entry)

def taskbar(session, caption, dialogs = [], context_menu = {}):
    entry = TaskbarEntry()
    entry.package_name = misc.getSource()
    entry.caption = caption
    entry.dialogs = dialogs
    entry.context_menu = context_menu
    session.jman_taskbar.append(entry)
