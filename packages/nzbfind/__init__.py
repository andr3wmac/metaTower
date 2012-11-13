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

def home(resp):
    resp.htmlFile("nzbfind/home.html", "container")
    resp.jsFile("nzbfind/script.js")
    resp.cssFile("nzbfind/style.css")

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
