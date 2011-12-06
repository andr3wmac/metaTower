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

    mt.log.error("SHIT WENT WRONG BRO!")

def jman_load(resp):
    mt.packages.jman.menu(resp.session, "File Manager", 3)
    mt.packages.jman.taskbar(resp.session, "File Manager", ['fileman_main'])
    resp.htmlFile("fileman/html/jman.html", "body", True)
    resp.jsFile("fileman/js/common.js")
    resp.jsFile("fileman/js/jman.js")
    resp.cssFile("fileman/css/style.css")

def jman_menu(resp):
    openFolder(resp, os.getcwd(), "files")
    resp.js("jman.dialog('fileman_main');")

def jmanlite_load(resp):
    mt.packages.jmanlite.menu(resp.session, "File Manager", "fileman")

def jmanlite_menu(resp):
    resp.htmlFile("fileman/html/jmanlite.html", "jmanlite_content", False)
    resp.jsFile("fileman/js/common.js")
    resp.jsFile("fileman/js/jmanlite.js")
    resp.cssFile("fileman/css/style.css")
    openFolder(resp, os.getcwd(), "files")
    
def openFolder(resp, path, folder):
    path = replaceHomeDir(resp.session, path)
    path = os.path.join(path, folder)
    listContents(resp, path)

def folderUp(resp, path):
    path = replaceHomeDir(resp.session, path)
    path = os.path.split(path)[0]
    listContents(resp, path)

def replaceHomeDir(session, path):
    result = ""
    home_dir = session.user.homedir
    if ( home_dir == "" ): home_dir = os.getcwd()
    else: home_dir = os.path.join(os.getcwd(), home_dir)

    if ( path[0] == "~" ):
        result = path.replace("~", home_dir)
    else:
        result = path.replace(home_dir, "~")
    return result

def listContents(resp, path):
    dir_html = ""
    file_html = ""
    for entry in getFileList(resp.session, path):
        if ( entry.is_dir ): dir_html += ",'" + entry.file_name + "'"
        if ( entry.is_file ): file_html += ",'" + entry.file_name + "'"
    path = path.replace("\\", "/")

    # shortens the path to ~ if its the users homedir.
    path = path = replaceHomeDir(resp.session, path)
    resp.js("fileman.data('" + path + "', [" + dir_html[1:] + "], [" + file_html[1:] + "]);")
    

