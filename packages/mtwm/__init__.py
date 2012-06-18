import time, mt

def onLoad():
    mt.events.register("mtwm.onIndex", onIndex)
    mt.events.register("mtwm.onPageLoad", home)

def onUnload():
    mt.events.clear(onIndex)
    mt.events.clear(home)

def onIndex(resp):
    resp.session.mtwm_menu = []
    resp.file("mtwm/index.html")

def home(resp):
    resp.htmlFile("mtwm/home.html", "container")
    resp.jsFile("mtwm/script.js")
    updateHome(resp)

def updateHome(resp):
    plist = "{"
    for package in mt.packages.list:
        mod = mt.packages.list[package]
        func = ""
        if ( hasattr(mod, "home") ): func = "mt('" + package + ".home()');"
        plist += "\"" + mod.name + "\": \"" + func + "\","
    plist = plist[:-1] + "}"

    free_space = mt.utils.convert_bytes(mt.utils.get_free_space())
    resp.js("mtwm.home.update(\"0.5\", " + plist + ", \"" + free_space + "\");")


class MenuEntry:
    caption = ""
    package_name = ""

def menu(session, caption, package_name):
    new_menu_entry = MenuEntry()
    new_menu_entry.caption = caption
    new_menu_entry.package_name = package_name
    session.mtwm_menu.append(new_menu_entry)
