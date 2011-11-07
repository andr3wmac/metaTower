import time
import mtCore as mt
import mtMisc as misc

def onLoad():
    mt.events.register("jmanlite.onIndex", onIndex)
    mt.events.register("jmanlite.onPageLoad", onPageLoad)

def onUnload():
    mt.events.clear(onIndex)
    mt.events.clear(onPageLoad)

def onIndex(session):
    session.jmanlite_menu = []
    out = session.out()
    out.file("jmanlite/index.html")
    return out
    
def onPageLoad(session):
    out = session.out()
    out.append(mt.events.trigger("jmanlite.load", session))
    menuJS = ""
    for entry in session.jmanlite_menu:
        menuJS += "jmanlite.menu('" + entry.caption + "', '" + entry.package_name + "');"
    out.js(menuJS)
    out.append(mt.events.trigger("jmanlite.menu.mbrowser", session))
    return out

class MenuEntry:
    caption = ""
    package_name = ""

def menu(session, caption, package_name):
    new_menu_entry = MenuEntry()
    new_menu_entry.caption = caption
    new_menu_entry.package_name = package_name
    session.jmanlite_menu.append(new_menu_entry)
