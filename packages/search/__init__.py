import mt

class SearchEngine():
    def __init__(self, name, query_fn, save_fn):
        self.name = name
        self.query_fn = query_fn
        self.save_fn = save_fn

    def query(self, content, filters):
        if ( self.query_fn ): return self.query_fn(content, filters)
        return []

    def save(self, query_id):
        if ( self.save_fn ): return self.save_fn(query_id)
        return False

engines = []
def onLoad():
    global engines

    if ( mt.packages.http ):
        http = mt.packages.http
        http.addFiles({
            "/search/images/mtfile.png": "packages/search/images/mtfile.png",
            "/search/images/mtfile_trans.png": "packages/search/images/mtfile_trans.png",
            "/search/images/icon.png": "packages/search/images/icon.png",
            "/search/script.js": "packages/search/script.js",
            "/search/style.css": "packages/search/style.css"
        })
        http.addScript("search/script.js")
        http.addStyle("search/style.css")

def addEngine(name, query_fn, save_fn):
    global engines

    new_engine = SearchEngine(name, query_fn, save_fn)
    engines.append(new_engine)

def home(httpOut):
    global engines

    httpOut.htmlFile("packages/search/home.html", "container")

    engine_list = []
    for engine in engines:
        engine_list.append(engine.name)

    httpOut.jsFunction("searchpkg.EngineList.set", engine_list)

def query(httpOut, content, engineIndex = -1, filters = ""):
    global engines
    results = {}

    engineNum = 0
    for engine in engines:
        if ( engineIndex > -1 ):
            if ( engineIndex == engineNum ): results[engineNum] = engine.query(content, filters)
            else: results[engineNum] = []
        else:
            results[engineNum] = engine.query(content, filters)            
        engineNum += 1

    httpOut.jsFunction("searchpkg.data", results)

def save(httpOut, query_id, engineIndex = -1):
    global engines
    success = False

    if ( engineIndex > -1 ):
        if ( engineIndex >= len(engines) ): 
            success = False
        else:
            engine = engines[engineIndex]
            success = engine.save(query_id)
    else:
        for engine in engines:
            result = engine.save(query_id)
            if result: success = True

    if success:
        httpOut.jsFunction("searchpkg.save_complete")
