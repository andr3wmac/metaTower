import os
import mtCore as mt

def onLoad():
    mt.events.register("jman.load", jman_load)
    mt.events.register("jman.menu.configmanager", jman_menu)

def jman_load(resp):
    mt.packages.jman.menu(resp.session, "Config Manager", 5)
    mt.packages.jman.taskbar(resp.session, "Config Manager", ['configmanager_main'])
    resp.htmlFile("configmanager/index.html", "body", True)
    resp.jsFile("configmanager/script.js")
    resp.cssFile("configmanager/style.css")

def jman_menu(resp):
    getConfigTree(resp)
    resp.js("jman.dialog('configmanager_main');")

def getConfigTree(resp):
    config_items = mt.config.items
    path_list = []
    value_list = []
    file_list = []
    for item in config_items:
        path_list.append(item.path)
        value_list.append(item)
        file_list.append(item.source_file)
    resp.js("configmanager.tree(" + str(path_list) + "," + str(value_list) + "," + str(file_list) + ");")

def save(resp, path, value, f):
    mt.config[path] = value
    mt.config[path].source_file = f
    getConfigTree(resp)
    

