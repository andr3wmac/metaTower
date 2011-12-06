import time
import mtCore as mt
import mtMisc as misc

def onLoad():
    mt.events.register("jmanlite.onIndex", onIndex)
    mt.events.register("jmanlite.onPageLoad", onPageLoad)

def onUnload():
    mt.events.clear(onIndex)
    mt.events.clear(onPageLoad)

def onIndex(resp):
    resp.session.jmanlite_menu = []
    resp.file("jmanlite/index.html")
    
def onPageLoad(resp):
    mt.events.trigger("jmanlite.load", resp.session)
    menuJS = ""
    for entry in resp.session.jmanlite_menu:
        menuJS += "jmanlite.menu('" + entry.caption + "', '" + entry.package_name + "');"
    resp.js(menuJS)
    mt.events.trigger("jmanlite.menu.mbrowser", resp.session)

class MenuEntry:
    caption = ""
    package_name = ""

def menu(session, caption, package_name):
    new_menu_entry = MenuEntry()
    new_menu_entry.caption = caption
    new_menu_entry.package_name = package_name
    session.jmanlite_menu.append(new_menu_entry)
