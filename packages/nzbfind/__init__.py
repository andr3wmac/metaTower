import mt, nzbmatrix

engine = None

def onLoad():
    global engine
    
    cfg = mt.config
    cfg.load("packages/nzbfind/sources.cfg")
    cfg.load("packages/nzbfind/downloaded.cfg", True)

    save_to = cfg["nzbfind/save_to"]

    if ( cfg["nzbfind/sources/nzbmatrix/username"] ):
        user = cfg["nzbfind/sources/nzbmatrix/username"]
        api = cfg["nzbfind/sources/nzbmatrix/api-key"]
        engine = nzbmatrix.NZBMatrix(user, api, save_to)

    mt.requests.addFile("GET", "/nzbfind/images/mtfile.png", "packages/nzbfind/images/mtfile.png")
    mt.requests.addFile("GET", "/nzbfind/images/mtfile_trans.png", "packages/nzbfind/images/mtfile_trans.png")

def home(resp):
    resp.htmlFile("packages/nzbfind/home.html", "container")
    resp.jsFile("packages/nzbfind/script.js")
    resp.cssFile("packages/nzbfind/style.css")

def search(resp, query, cat):
    global engine
    if ( not engine ): 
        resp.js("nzbfind.data({})")
        return

    dlist = []
    config_list = mt.config.get("nzbfind/downloaded/nzb")
    for item in config_list:
        dlist.append(item["id"])

    results = engine.search(query, cat)
    formatted_results = []
    for r in results:
        formatted_results.append({"id": r.id, "name": r.name, "size": r.size, "downloaded": str(str(r.id) in dlist)})
    
    resp.js("nzbfind.data(" + str(formatted_results) + ");")

def download(resp, id):
    global engine

    # generate a list of files from the known library
    found = False
    config_list = mt.config.get("nzbfind/downloaded/nzb")
    for item in config_list:
        if ( item["id"] == str(id) ): found = True
    
    if ( not found ):
        element = mt.config.ConfigItem("")
        element["id"] = str(id)
        mt.config.add(element, "nzbfind/downloaded/nzb", "packages/nzbfind/downloaded.cfg")
        mt.config.save("packages/nzbfind/downloaded.cfg")

    resp.js("nzbfind.dl_complete()")
    if ( not engine ): return
    engine.download(id)
