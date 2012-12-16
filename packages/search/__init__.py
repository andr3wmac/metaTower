import mt

class SearchEngine():
    def __init__(self, name, search_fn, save_fn):
        self.name = name
        self.search_fn = search_fn
        self.save_fn = save_fn

    def search(self, query):
        if ( self.search_fn ): return self.search_fn(query)
        return []

    def save(self, query_id):
        if ( self.save_fn ): return self.save_fn(query_id)
        return False

engines = []
def onLoad():
    global engines

    if ( mt.packages.http ):
        http = mt.packages.http
        http.addFile("/search/images/mtfile.png", "packages/search/images/mtfile.png")
        http.addFile("/search/images/mtfile_trans.png", "packages/search/images/mtfile_trans.png")
        http.addFile("/search/images/icon.png", "packages/search/images/icon.png")

def addEngine(name, search_fn, save_fn):
    global engines

    new_engine = SearchEngine(name, search_fn, save_fn)
    engines.append(new_engine)

def home(resp):
    global engines

    resp.htmlFile("packages/search/home.html", "container")
    resp.jsFile("packages/search/script.js")
    resp.cssFile("packages/search/style.css")

    engine_list = []
    for engine in engines:
        engine_list.append(engine.name)
    resp.jsFunction("search.setEngines", engine_list)

def search(resp, query):
    global engines

    results = []
    for engine in engines:
        results += engine.search(query)    

    resp.jsFunction("search.data", results)
