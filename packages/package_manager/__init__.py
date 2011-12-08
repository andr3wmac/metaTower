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
    cfg.load("packages/package_manager/sources.cfg")

    mt.events.register("jman.load", jman_load)
    mt.events.register("jman.menu.package_manager", jman_menu)

def onUnload():
    mt.events.clear(jman_load)
    mt.events.clear(jman_menu)

def getPackageInfo(resp, package_id):
    for package in mt.packages.list:
        pack = mt.packages.list[package]
        if ( pack.id == package_id ):
            resp.js("package_manager.data('" + package_id + "', '" + pack.name + "', 0, '" + pack.version + "', '" + mt.config[package_id + "/description"] + "');");

def getUpdateInfo(resp, package_id):
    global package_list
    for package in package_list:
        if ( package.id == package_id ):
            resp.js("package_manager.data('" + package_id + "', '" + package.name + "', 1, '" + package.version + "', '" + package.description + "');");

def getInstallInfo(resp, package_id):
    global package_list
    for package in package_list:
        if ( package.id == package_id ):
            resp.js("package_manager.data('" + package_id + "', '" + package.name + "', 2, '" + package.version + "', '" + package.description + "');");

def update(resp, package_id):
    global package_list, package_downloader
    if ( package_downloader != None ): return

    package_path = "packages"
    for package in package_list:
        if ( package.id == package_id ):
            package_downloader = PackageDownloader(dlStatus, dlInstallComplete, dlUpdateComplete)
            package_downloader.updatePackage(package)
            setStatus("Starting update..", 0)
    status(resp)

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

def status(resp):
    global current_status, current_progress
    resp.js("package_manager.statusUpdate(\"" + current_status + "\", " + str(current_progress) + ");")
    if ( current_progress >= 100 ):
        resp.js("mt.refresh()")

def install(resp, package_id):
    global package_list, package_downloader
    if ( package_downloader != None ): return

    package_path = "packages"
    for package in package_list:
        if ( package.id == package_id ):
            package_downloader = PackageDownloader(dlStatus, dlInstallComplete, dlUpdateComplete)
            if ( package_downloader.installPackage(package) ):
                setStatus("Starting install..", 0)
            else:
                setStatus("Error installing package.", 0)
                package_downloader = None
    status(resp)

def delete(resp, package_id):
    path = os.path.join("packages", package_id)
    if ( os.path.isdir(path) ):
        mtMisc.rmdir(path)
        mt.packages.unload(package_id)
        resp.js("package_manager.status('Package deleted. Refreshing...');")
        resp.js("mt.refresh();")
    else:
        resp.js("package_manager.status('Could not delete, folder not found.');")

def refresh(resp):
    _refreshSources()
    packageListOut(resp)
    resp.js("package_manager.status('Sources up to date.', 100);")

def httpGet(url):
    data = None
    try:
        http = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPCookieProcessor())
        response = http.open(url)
        data = response.read()
    except:
        mt.log.error("HTTP Get Failed: " + url)
        data = None
    return data

def _refreshSources():
    global package_list
    package_list = []
    source_list = mt.config["package_manager/sources"].replace(" ", "").replace("\t", "").replace("\n", "").split(",")
    for source in source_list:
        package_list += _querySource(source)

def _querySource(source):
    results = []
    if ( not source.lower().startswith("http://") ): return results

    source_args = source.split("/")
    if ( source.endswith("/") ):
        source_root = source
    else:
        if ( len(source_args) == 3 ):
            source_root = source + "/"
        else:
            source_root = "/".join(source_args[:-1])
        
    data = httpGet(source)
    if ( data == None ): return results

    if ( data.lower().startswith("http://") ) or ( data[:2] == "./" ):
        urls = data.split("\n")
        for url in urls:
            if ( url[:2] == "./" ):
                results += _querySource(source_root + url)
            if ( url.lower().startswith("http://") ):
                results += _querySource(url)
    else:
        tree = ElementTree.fromstring(mt.config.header + data + mt.config.footer)
        for element in tree:
            pack = Package()
            pack.id = element.tag
            for attr in element:
                attr.text = attr.text.strip()
                if ( attr.tag == "name" ): pack.name = attr.text
                if ( attr.tag == "version" ): pack.version = attr.text
                if ( attr.tag == "description" ): pack.description = attr.text
                if ( attr.tag == "source_url" ): pack.source_url = attr.text
                if ( attr.tag == "install_files" ): pack.install_files = attr.text.replace(" ", "").replace("\t", "").replace("\n", "").split(",")
                if ( attr.tag == "update_files" ): pack.update_files = attr.text.replace(" ", "").replace("\t", "").replace("\n", "").split(",")
            results.append(pack)
    return results

def jman_load(resp):
    mt.packages.jman.menu(resp.session, "Package Manager", 5)
    mt.packages.jman.taskbar(resp.session, "Package Manager", ['package_manager_main'])
    resp.htmlFile("package_manager/html/jman.html", "body", True)
    resp.jsFile("package_manager/js/common.js")
    resp.jsFile("package_manager/js/jman.js")
    resp.cssFile("package_manager/css/style.css")

def jman_menu(resp):
    resp.js("jman.dialog('package_manager_main');")
    resp.js("package_manager.refresh();")

def packageListOut(resp):
    global package_list

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

    resp.js("package_manager.packageList(" + str(installed_packages) + "," + str(updates) + "," + str(available_packages) + ")")

