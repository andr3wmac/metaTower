import mt, nzbmatrix

engine = None

def onLoad():
    global engine
    
    cfg = mt.config
    cfg.load("packages/nzbfind/sources.cfg")

    save_to = cfg["nzbfind/save_to"]

    if ( cfg["nzbfind/sources/nzbmatrix/username"] ):
        user = cfg["nzbfind/sources/nzbmatrix/username"]
        api = cfg["nzbfind/sources/nzbmatrix/api-key"]
        engine = nzbmatrix.NZBMatrix(user, api, save_to)

    mt.events.register("jman.load", jman_load)
    mt.events.register("jman.menu.nzbfind", jman_menu)

    mt.events.register("jmanlite.load", jmanlite_load)
    mt.events.register("jmanlite.menu.nzbfind", jmanlite_menu)

def onUnload():
    mt.events.clear(jman_load)
    mt.events.clear(jman_menu)

def jman_load(resp):
    mt.packages.jman.menu(resp.session, "NZB Find", 5)
    mt.packages.jman.taskbar(resp.session, "NZB Find", ['nzbfind_main'])
    resp.htmlFile("nzbfind/html/jman.html", "body", True)
    resp.jsFile("nzbfind/js/common.js")
    resp.jsFile("nzbfind/js/jman.js")
    resp.cssFile("nzbfind/css/style.css")

def jman_menu(resp):
    resp.js("jman.dialog('nzbfind_main');")
    #resp.js("package_manager.refresh();")

def jmanlite_load(resp):
    mt.packages.jmanlite.menu(resp.session, "NZB Find", "nzbfind")

def jmanlite_menu(resp):
    resp.htmlFile("nzbfind/html/jmanlite.html", "jmanlite_content", False)
    resp.jsFile("nzbfind/js/common.js")
    resp.jsFile("nzbfind/js/jmanlite.js")
    resp.cssFile("nzbfind/css/style.css")

def search(resp, query, cat):
    global engine
    if ( not engine ): 
        resp.js("nzbfind.data({})")
        return

    results = engine.search(query, cat)
    formatted_results = []
    for r in results:
        formatted_results.append({"id": r.id, "name": r.name, "size": r.size})

    resp.js("nzbfind.data(" + str(formatted_results) + ");")

def download(resp, id):
    global engine
    resp.js("nzbfind.dl_complete()")
    if ( not engine ): return
    engine.download(id)
