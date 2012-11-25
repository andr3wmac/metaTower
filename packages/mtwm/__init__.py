import time, mt

def onLoad():
    mt.requests.addFunction("GET", "/", onIndex)   
    mt.requests.addFile("GET", "/mtwm/quickbar.css", "packages/mtwm/quickbar.css")    
    mt.requests.addFile("GET", "/mtwm/style.css", "packages/mtwm/style.css")
    mt.requests.addFile("GET", "/mtwm/theme.css", "packages/mtwm/theme.css")
    mt.requests.addFile("GET", "/mtwm/mtwm.js", "packages/mtwm/mtwm.js")
    mt.requests.addFile("GET", "/mtwm/images/menu_bg.png", "packages/mtwm/images/menu_bg.png")
    mt.requests.addFile("GET", "/mtwm/images/tower.png", "packages/mtwm/images/tower.png") 
    mt.requests.addFile("GET", "/mtwm/images/content_bg.png", "packages/mtwm/images/content_bg.png") 

#def onUnload():
#    mt.events.clear(onIndex)
#    mt.events.clear(home) 

def onIndex(resp):
    resp.session.mtwm_menu = []
    resp.file("packages/mtwm/index.html")

def home(resp):
    resp.htmlFile("packages/mtwm/home.html", "container")
    resp.jsFile("packages/mtwm/script.js")
    updateHome(resp)

def updateHome(resp):
    plist = "{"

    for package in mt.packages.list:
        if ( mt.config[package + "/hidden"] ):
            continue

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
