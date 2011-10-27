import time
import mtCore as mt
import mtMisc as misc

def onLoad():
    mt.events.register("jman.onIndex", onIndex)
    mt.events.register("jman.onPageLoad", onPageLoad)

def onUnload():
    mt.events.clear(onIndex)
    mt.events.clear(onPageLoad)

def onIndex(session):
    session.jman_menu = []
    session.jman_taskbar = []
    out = session.out()
    out.file("jman/index.html")
    return out
    
def onPageLoad(session):
    out = session.out()
    out.append(mt.events.trigger("jman.load", session))

    # dump menu data
    menuJS = ""
    for entry in session.jman_menu:
        menuJS += "jman.menu.add('" + entry.package_name  + "', '" + entry.caption + "', " + str(entry.priority) + ", '" + entry.onClick + "');"
    out.js(menuJS)

    # dump package data
    packageJS = ""
    for entry in session.jman_taskbar:
        packageJS += "jman.taskbar.add('" + entry.package_name + "', '" + entry.caption + "', " + str(entry.dialogs) + ", " + str(entry.context_menu) + ");"
    out.js(packageJS)
    return out

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

def menu(session, caption, priority = 5, onClick = ""):
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
