import os, mt

def onLoad():
    mt.events.register("jman.load", jman_load)
    mt.events.register("jman.menu.confedit", jman_menu)

def jman_load(resp):
    mt.packages.jman.menu(resp.session, "Configuration", 5)
    mt.packages.jman.taskbar(resp.session, "Configuration", ['confedit_main'])
    resp.htmlFile("confedit/index.html", "body", True)
    resp.jsFile("confedit/script.js")
    resp.cssFile("confedit/style.css")

def jman_menu(resp):
    getConfigTree(resp)
    resp.js("jman.dialog('confedit_main');")

def getConfigTree(resp):
    config_items = mt.config.items
    path_list = []
    value_list = []
    file_list = []
    for item in config_items:
        path_list.append(item.path)
        value_list.append(item)
        file_list.append(item.source_file)
    resp.js("confedit.tree(" + str(path_list) + "," + str(value_list) + "," + str(file_list) + ");")

def save(resp, path, value, f):
    mt.config[path] = value
    mt.config[path].source_file = f
    getConfigTree(resp)
    

