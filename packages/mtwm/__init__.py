import time, mt

def onLoad():   
    mt.config.load("packages/mtwm/mtwm.cfg")
 
    if ( mt.packages.http ):
        mt.events.register("HTTP GET /", onIndex)

        http = mt.packages.http       
        http.addFile("/mtwm/quickbar.css", "packages/mtwm/quickbar.css")    
        http.addFile("/mtwm/style.css", "packages/mtwm/style.css")
        http.addFile("/mtwm/theme.css", "packages/mtwm/theme.css")
        http.addFile("/mtwm/mtwm.js", "packages/mtwm/mtwm.js")
        http.addFile("/mtwm/images/menu_bg.png", "packages/mtwm/images/menu_bg.png")
        http.addFile("/mtwm/images/tower.png", "packages/mtwm/images/tower.png") 
        http.addFile("/mtwm/images/hdd.png", "packages/mtwm/images/hdd.png") 
        http.addFile("/mtwm/images/content_bg.png", "packages/mtwm/images/content_bg.png") 
        http.addFile("/mtwm/images/pin.png", "packages/mtwm/images/pin.png")
        http.addFile("/mtwm/images/pin_trans.png", "packages/mtwm/images/pin_trans.png")

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
    # output quickbar.
    qbar_list = mt.config["mtwm/quickbar"].split(",")

    # output packages.
    plist = {}
    for package in mt.packages.list:
        if ( mt.config[package + "/hidden"] ):
            continue

        mod = mt.packages.list[package]
        func = ""
        if ( hasattr(mod, "home") ): func = "mt('" + package + ".home()');"
        plist[package] = [mod.name, func, package in qbar_list]

    # HDD widget.
    hdds = mt.utils.get_hdds()
    resp.jsFunction("mtwm.home.updateHDDWidget", hdds)

    # function.    
    resp.jsFunction("mtwm.home.update", 0.5, plist, qbar_list)

def togglePin(httpOut, package_name):
    qbar_list = mt.config["mtwm/quickbar"].split(",")

    if ( package_name in qbar_list ):
        qbar_list.remove(package_name)
    else:
        qbar_list.append(package_name)

    mt.config["mtwm/quickbar"] = ",".join(qbar_list)
    
    updateHome(httpOut)    
    mt.config.save("packages/mtwm/mtwm.cfg")

class MenuEntry:
    caption = ""
    package_name = ""

def menu(session, caption, package_name):
    new_menu_entry = MenuEntry()
    new_menu_entry.caption = caption
    new_menu_entry.package_name = package_name
    session.mtwm_menu.append(new_menu_entry)
