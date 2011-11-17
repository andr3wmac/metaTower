import os, re, time, string, urllib2
import xml.etree.ElementTree as ElementTree
import mtConfigManager, mtMisc
import mtCore as mt
from downloader import PackageDownloader

package_list = []
package_downloader = None
current_status = ""
current_percent = 0

class Package:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.version = "0.0"
        self.path = ""
        self.description = ""
        self.source_url = ""
        self.install_files = []
        self.update_files = []

def onLoad():
    cfg = mt.config
    cfg.load("packages/package_manager/sources.xml")

    mt.events.register("jman.load", jman_load)
    mt.events.register("jman.menu.package_manager", jman_menu)

def onUnload():
    mt.events.clear(jman_load)
    mt.events.clear(jman_menu)

def getPackageInfo(session, package_id):
    out = session.out()
    for package in mt.packages.list:
        pack = mt.packages.list[package]
        if ( pack.id == package_id ):
            out.js("package_manager.data('" + package_id + "', '" + pack.name + "', 0, '" + pack.version + "', '" + mt.config[package_id + "/description"] + "');");
    return out

def getUpdateInfo(session, package_id):
    global package_list
    out = session.out()
    for package in package_list:
        if ( package.id == package_id ):
            out.js("package_manager.data('" + package_id + "', '" + package.name + "', 1, '" + package.version + "', '" + package.description + "');");
    return out

def getInstallInfo(session, package_id):
    global package_list
    out = session.out()
    for package in package_list:
        if ( package.id == package_id ):
            out.js("package_manager.data('" + package_id + "', '" + package.name + "', 2, '" + package.version + "', '" + package.description + "');");
    return out

def update(session, package_id):
    global package_list, package_downloader
    if ( package_downloader != None ): return

    package_path = "packages"
    for package in package_list:
        if ( package.id == package_id ):
            package_downloader = PackageDownloader(dlStatus, dlInstallComplete, dlUpdateComplete)
            package_downloader.updatePackage(package)
            setStatus("Starting update..", 0)
    return status(session)

def dlStatus(package, queued, completed):
    setStatus("Downloading..", int(float(completed)/float(queued)*100))

def dlInstallComplete(package):
    global package_downloader
    mt.packages.load(package.id, "packages")
    setStatus("Install Complete, Refreshing.", 100)
    package_downloader = None

def dlUpdateComplete(package):
    global package_downloader
    mt.packages.load(package.id, "packages")
    setStatus("Update Complete, Refreshing.", 100)
    package_downloader = None

def setStatus(status, progress):
    global current_status, current_progress
    current_status = status
    current_progress = progress

def status(session):
    global current_status, current_progress
    out = session.out()
    out.js("package_manager.statusUpdate(\"" + current_status + "\", " + str(current_progress) + ");")
    if ( current_progress >= 100 ):
        out.js("mt.refresh()")
    return out

def install(session, package_id):
    global package_list, package_downloader
    if ( package_downloader != None ): return

    package_path = "packages"
    for package in package_list:
        if ( package.id == package_id ):
            package_downloader = PackageDownloader(dlStatus, dlInstallComplete, dlUpdateComplete)
            package_downloader.installPackage(package)
            setStatus("Starting install..", 0)
    return status(session)

def delete(session, package_id):
    out = session.out()
    path = os.path.join("packages", package_id)
    if ( os.path.isdir(path) ):
        mtMisc.rmdir(path)
        mt.packages.unload(package_id)
        out.js("package_manager.status('Package deleted. Refreshing...');")
        out.js("mt.refresh();")
    else:
        out.js("package_manager.status('Could not delete, folder not found.');")
    return out

def refresh(session):
    out = session.out()
    _refreshSources()
    #out.append(mainMenu(session))
    out.append(packageListOut(session))
    out.js("package_manager.status('Sources up to date.', 100);")
    return out

def httpGet(url):
    data = ""
    try:
        http = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPCookieProcessor())
        response = http.open(url)
        data = response.read()
    except:
        print "HTTP GET FAILED: " + url
        data = ""
    return data

def _refreshSources():
    global package_list
    
    data = httpGet("http://packages.metatower.com/packages.php?x=all")
    package_list = []
    tree = ElementTree.fromstring(data)
    for element in tree:
        pack = Package()
        pack.id = element.tag
        for attr in element:
            if ( attr.tag == "name" ): pack.name = attr.text
            if ( attr.tag == "version" ): pack.version = attr.text
            if ( attr.tag == "description" ): pack.description = attr.text
            if ( attr.tag == "source_url" ): pack.source_url = attr.text
            if ( attr.tag == "install_files" ): pack.install_files = attr.text.replace(" ", "").replace("\t", "").replace("\n", "").split(",")
            if ( attr.tag == "update_files" ): pack.update_files = attr.text.replace(" ", "").replace("\t", "").replace("\n", "").split(",")
        package_list.append(pack)

def jman_load(session):
    mt.packages.jman.menu(session, "Package Manager", 0)
    mt.packages.jman.taskbar(session, "Package Manager", ['package_manager_main'])
    out = session.out()
    out.htmlFile("package_manager/html/jman.html", "body", True)
    out.jsFile("package_manager/js/common.js")
    out.jsFile("package_manager/js/jman.js")
    out.cssFile("package_manager/css/style.css")
    return out

def jman_menu(session):
    out = session.out()
    out.js("jman.dialog('package_manager_main');")
    out.js("package_manager.refresh();")
    return out

def packageListOut(session):
    global package_list
    out = session.out()

    # for each installed package
    installed_packages = {}
    for package_id in mt.packages.list:
        package = mt.packages.list[package_id]
        installed_packages[package_id] = package.name

    # for each package in from sources.xml
    updates = {}
    available_packages = {}
    for source_package in package_list:

        # for each installed package.
        installed = False
        for package_id in mt.packages.list:
            package = mt.packages.list[package_id]
            if ( package.id == source_package.id ):
                installed = True
                if ( float(package.version) < float(source_package.version) ):
                    updates[package.id] = package.name
        if ( not installed ):
            available_packages[source_package.id] = source_package.name

    out.js("package_manager.packageList(" + str(installed_packages) + "," + str(updates) + "," + str(available_packages) + ")")
    return out

