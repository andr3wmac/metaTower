import time, mt

def onLoad():    
    if ( mt.packages.http ):
        mt.events.register("HTTP GET /", onIndex)

        http = mt.packages.http       
        http.addFile("/mtwm/quickbar.css", "packages/mtwm/quickbar.css")    
        http.addFile("/mtwm/style.css", "packages/mtwm/style.css")
        http.addFile("/mtwm/theme.css", "packages/mtwm/theme.css")
        http.addFile("/mtwm/mtwm.js", "packages/mtwm/mtwm.js")
        http.addFile("/mtwm/images/menu_bg.png", "packages/mtwm/images/menu_bg.png")
        http.addFile("/mtwm/images/tower.png", "packages/mtwm/images/tower.png") 
        http.addFile("/mtwm/images/content_bg.png", "packages/mtwm/images/content_bg.png") 

#def onUnload():
#    mt.events.clear(onIndex)
#    mt.events.clear(home) 

def onIndex(httpIn, httpOut):
    httpIn.session.mtwm_menu = []
    httpOut.file("packages/mtwm/index.html")

def home(resp):
    resp.htmlFile("packages/mtwm/home.html", "container")
    resp.jsFile("packages/mtwm/script.js")
    updateHome(resp)

def updateHome(resp):
    plist_out = "{}"
    plist = []
    for package in mt.packages.list:
        if ( mt.config[package + "/hidden"] ):
            continue

        mod = mt.packages.list[package]
        func = ""
        if ( hasattr(mod, "home") ): func = "mt('" + package + ".home()');"
        plist.append("\"" + mod.name + "\": \"" + func + "\"")
    plist_out = "{" + ",".join(plist) + "}"
    
    free_space = mt.utils.convert_bytes(mt.utils.get_free_space())
    resp.js("mtwm.home.update(\"0.5\", " + plist_out + ", \"" + free_space + "\");")


class MenuEntry:
    caption = ""
    package_name = ""

def menu(session, caption, package_name):
    new_menu_entry = MenuEntry()
    new_menu_entry.caption = caption
    new_menu_entry.package_name = package_name
    session.mtwm_menu.append(new_menu_entry)
