import os
import mtCore as mt

class fmanEntry:
    def __init__(self):
        self.is_dir = False
        self.is_file = False
        self.file_name = ""
        
def getFileList(session, path):
    results = []
    for f in os.listdir(path):
        ff = os.path.join(path,f)
        newEntry = fmanEntry()
        if os.path.isdir(ff): newEntry.is_dir = True
        if os.path.isfile(ff): newEntry.is_file = True
        newEntry.path = path
        newEntry.file_name = f
        results.append(newEntry)
    return results

def onLoad():
    mt.events.register("jman.load", jman_load)
    mt.events.register("jman.menu.fileman", jman_menu)

    mt.events.register("jmanlite.load", jmanlite_load)
    mt.events.register("jmanlite.menu.fileman", jmanlite_menu)

def jman_load(session):
    mt.packages.jman.menu(session, "File Manager", 3)
    mt.packages.jman.taskbar(session, "File Manager", ['fileman_main'])
    out = session.out()
    out.htmlFile("fileman/html/jman.html", "body", True)
    out.jsFile("fileman/js/common.js")
    out.jsFile("fileman/js/jman.js")
    out.cssFile("fileman/css/style.css")
    return out

def jman_menu(session):
    out = session.out()
    out.append(openFolder(session, os.getcwd(), "files"))
    out.js("jman.dialog('fileman_main');")
    return out

def jmanlite_load(session):
    mt.packages.jmanlite.menu(session, "File Manager", "fileman")
    return None

def jmanlite_menu(session):
    out = session.out()
    out.htmlFile("fileman/html/jmanlite.html", "jmanlite_content", False)
    out.jsFile("fileman/js/common.js")
    out.jsFile("fileman/js/jmanlite.js")
    out.cssFile("fileman/css/style.css")
    out.append(openFolder(session, os.getcwd(), "files"))
    return out
    
def openFolder(session, path, folder):
    path = os.path.join(path, folder)
    return listContents(session, path)

def folderUp(session, path):
    path = os.path.split(path)[0]
    return listContents(session, path)

def listContents(session, path):
    dir_html = ""
    file_html = ""
    for entry in getFileList(session, path):
        if ( entry.is_dir ): dir_html += ",'" + entry.file_name + "'"
        if ( entry.is_file ): file_html += ",'" + entry.file_name + "'"
    out = session.out()
    path = path.replace("\\", "/")
    out.js("fileman.data('" + path + "', [" + dir_html[1:] + "], [" + file_html[1:] + "]);")
    return out
    

