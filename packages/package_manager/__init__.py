import os, re, time, string, urllib2
import xml.etree.ElementTree as ElementTree
import mtConfigManager
import mtCore as mt

package_list = []
class Package:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.version = "0.0"
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
    global package_list
    package_path = "packages"
    out = session.out()
    for package in package_list:
        if ( package.id == package_id ):
            print "Updating " + package.name
            if ( package.source_url != "" ):
                for update_file in package.update_files:
                    url = package.source_url + package_id + "/" + update_file
                    path = os.path.join(package_path, package_id, update_file)
                    saveFile(url, path)
            mt.packages.reload(package_id)
            print "Package updated."
    out.js("mt.refresh()")
    return out

def deleteFolder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            if os.path.isdir(file_path):
                deleteFolder(file_path)
        except Exception, e:
            print e
    os.rmdir(folder)

def saveFile(url, file_path):
    path = os.path.split(file_path)[0]
    if ( not os.path.isfile(file_path) ):
        if ( not path == "" ) and ( not os.path.isdir(path) ):
            os.makedirs(path)
    data = httpGet(url)
    if ( data == "" ): raise IOError
    f = open(file_path, 'wb')
    f.write(data)
    f.close()

def install(session, package_id):
    global package_list
    package_path = "packages"
    out = session.out()
    try:
        for package in package_list:
            if ( package.id == package_id ):
                print "Installing " + package.name
                if ( package.source_url != "" ):
                    for install_file in package.install_files:
                        url = package.source_url + package_id + "/" + install_file
                        path = os.path.join(package_path, package_id, install_file)
                        saveFile(url, path)
                mt.packages.load(package_id, package_path)
                out.js("package_manager.status('Install success. Refreshing browser..');")
        out.js("mt.refresh()")
    except IOError:
        deleteFolder(os.path.join(package_path,package_id))
        out.js("package_manager.status('Installation failed. Missing files.');")
    
    return out

def delete(session, package_id):
    out = session.out()
    path = os.path.join("packages", package_id)
    if ( os.path.isdir(path) ):
        deleteFolder(path)
        mt.packages.unload(package_id)
        out.js("package_manager.status('Package deleted. Restarting metaTower, please wait.');")
        out.js("mt.refresh();")
    else:
        out.js("package_manager.status('Could not delete, folder not found.');")
    return out

def refresh(session):
    out = session.out()
    _refreshSources()
    out.append(mainMenu(session))
    out.js("package_manager.status('Sources up to date.');")
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

def mainMenu(session):
    global package_list

    out = session.out()
    installed_html = "<li class='cat'>Installed Packages</li>"
    update_html = "<li class='cat'>Updates Available</li>"
    available_html = "<li class='cat'>Available Packages</li>"

    # for each installed package
    for package_name in mt.packages.list:
        package = mt.packages.list[package_name]
        installed_html += "<li class='subcat' onClick='package_manager.getPackageInfo(\"" + package_name + "\");'>" + package.name + " v" + package.version + "</li>"

    # for each package in from sources.xml
    for source_package in package_list:
        # for each installed package.
        installed = False
        for package_name in mt.packages.list:
            package = mt.packages.list[package_name]
            if ( package.id == source_package.id ):
                installed = True
                if ( float(package.version) < float(source_package.version) ):
                    update_html += "<li class='subcat' onClick='package_manager.getUpdateInfo(\"" + source_package.id + "\");'>" + source_package.name + " v" + source_package.version + "</li>"
        if ( not installed ):
            available_html += "<li class='subcat' onClick='package_manager.getInstallInfo(\"" + source_package.id + "\");'>" + source_package.name + " v" + source_package.version + "</li>"
    out.html(installed_html + update_html + available_html, "package_manager_menu", False)
    return out

