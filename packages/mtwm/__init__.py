import time, mt, DefaultWidgets

def onLoad():   
    mt.config.load("packages/mtwm/mtwm.cfg")
 
    if not mt.packages.isLoaded("http"): return
    http = mt.packages.http
    http.addScript("mtwm/mtwm.js")
    http.addStyles([
        "mtwm/style.css",
        "mtwm/quickbar.css",
        "mtwm/theme.css"
    ])
    http.addFiles({
        "/mtwm/quickbar.css":           "packages/mtwm/quickbar.css",    
        "/mtwm/style.css":              "packages/mtwm/style.css",
        "/mtwm/theme.css":              "packages/mtwm/theme.css",
        "/mtwm/mtwm.js":                "packages/mtwm/mtwm.js",
        "/mtwm/script.js":              "packages/mtwm/script.js",
        "/mtwm/images/home.png":        "packages/mtwm/images/home.png",
        "/mtwm/images/menu_bg.png":     "packages/mtwm/images/menu_bg.png",
        "/mtwm/images/tower.png":       "packages/mtwm/images/tower.png", 
        "/mtwm/images/hdd.png":         "packages/mtwm/images/hdd.png", 
        "/mtwm/images/cpu.png":         "packages/mtwm/images/cpu.png", 
        "/mtwm/images/ram.png":         "packages/mtwm/images/ram.png",
        "/mtwm/images/content_bg.png":  "packages/mtwm/images/content_bg.png", 
        "/mtwm/images/pin.png":         "packages/mtwm/images/pin.png",
        "/mtwm/images/pin_trans.png":   "packages/mtwm/images/pin_trans.png"
    })

    addWidget(DefaultWidgets.SystemMonitor())

widgets = {}
def addWidget(widget):
    global widgets
    widgets[widget.name] = widget    

def home(httpOut):
    httpOut.htmlFile("packages/mtwm/home.html", "body")
    
    # process widgets
    for name in widgets:
        widget = widgets[name]
        widget.home(httpOut)

    # fill in the data.
    update(httpOut)

def update(httpOut):
    global widgets

    # output quickbar.
    qbar_list = []    
    config_list = mt.config.get("mtwm/quickbar/item")
    for item in config_list:
        qbar_list.append(item["package_name"])

    # output packages.
    plist = {}
    for package in mt.packages.list:
        if ( mt.config[package + "/hidden"] ):
            continue

        mod = mt.packages.list[package]
        func = ""
        if ( hasattr(mod, "home") ): func = "mt('" + package + ".home()');"
        plist[package] = [mod.name, func, package in qbar_list]
 
    httpOut.jsFunction("mtwm.home.update", 0.5, plist, qbar_list)
    
    # update widgets
    for name in widgets:
        widget = widgets[name]
        widget.update(httpOut)    

def togglePin(httpOut, package_name):
    found = False

    config_list = mt.config.get("mtwm/quickbar/item")
    mt.config.clear("mtwm/quickbar")
    for item in config_list:
        if ( item["package_name"] == package_name ): 
            found = True
        else:
            mt.config.add(item, "mtwm/quickbar/item", "packages/mtwm/mtwm.cfg")    
    
    if ( not found ):
        element = mt.config.ConfigItem("")
        element["package_name"] = package_name
        mt.config.add(element, "mtwm/quickbar/item", "packages/mtwm/mtwm.cfg")

    mt.config.save("packages/mtwm/mtwm.cfg")
    update(httpOut)    
