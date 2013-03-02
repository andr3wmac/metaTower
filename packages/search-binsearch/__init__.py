import mt, os, urllib

nzb_list = []
class NZBResult:
    def __init__(self, query_id, name, server = ""):
        self.query_id = query_id
        self.name = name
        self.server = server

def onLoad():
    mt.config.load("packages/search-binsearch/search-binsearch.cfg")
    mt.config.load("packages/search-binsearch/downloaded.cfg", True)

    if mt.packages.search:
        mt.packages.search.addEngine("binsearch.info", query, save)

def _queryBin(query_parms, downloaded):
    global nzb_list

    query_string = urllib.urlencode(query_parms)        
    url = "http://binsearch.info/?" + query_string
    data = mt.utils.openURL(url)

    result_list = []
    data = data.split("<td><input type=\"checkbox\" name=\"")

    if ( len(data) > 3 ):
        data = data[2:-1]
        for raw_nzb in data:
            raw_nzb = raw_nzb.split("\" ><td><span class=\"s\">")
            
            result = {}
            result["id"] = int(raw_nzb[0])

            # name of the result.
            raw_name = raw_nzb[1].split("</span>")[0].split("&quot;")
            clean_name = raw_name[0]            
            if len(raw_name) > 1: clean_name = raw_name[1]
            result["name"] = clean_name

            # try for size
            a = raw_nzb[1].split("size: ")
            if ( len(a) > 1 ):
                result["size"] = a[1].split(", parts")[0].replace("&nbsp;", " ")
                result_parts = result["size"].split(" ")
                if ( result_parts[1] == "KB" ):
                    result["size"] = str( round( float(result_parts[0])/1000, 2 ) ) + " MB"
            else:
                continue

            result["downloaded"] = str(result["id"]) in downloaded
            result_list.append(result)
            nzb_list.append(NZBResult(result["id"], result["name"], query_parms["server"]))

    return result_list

def query(content, filters = ""):
    global nzb_list
    nzb_list = []

    # get list of previously downloaded nzbs
    dlist = []
    config_list = mt.config.get("search-binsearch/downloaded/nzb")
    for item in config_list:
        dlist.append(item["id"])

    # filters and query parms
    query_parms = {
            "q": content, 
            "max": "50", 
            "adv_sort": "date"
        }

    # 0 : Over 100mb
    if ( "0," in filters ): query_parms["minsize"] = "100"
    # 1 : Over 500mb
    if ( "1," in filters ): query_parms["minsize"] = "500"
    # 2 : Over 1GB
    if ( "2," in filters ): query_parms["minsize"] = "1000"    

    results = []

    # query server 2 (often better results)
    query_parms["server"] = "2"
    results += _queryBin(query_parms, dlist)
    
    # query server 1
    query_parms["server"] = ""
    results += _queryBin(query_parms, dlist)

    return results

def save(query_id):
    global nzb_list

    # determine name of file.
    nzb_name = str(query_id) + ".nzb"
    server = ""
    for n in nzb_list:
        if ( int(n.query_id) == int(query_id) ): 
            nzb_name = n.name + ".nzb"
            server = n.server   

    # fetch file.
    url = "http://binsearch.info/fcgi/nzb.fcgi?server=" + server
    post_data = str(query_id) + "=on&action=nzb"    
    data = mt.utils.openURL(url, post_data)

    # save.
    f = open(os.path.join(mt.config["search-binsearch/save_to"], nzb_name), "w")
    f.write(data)
    f.close()

    # keep track of the ones we've downloaded already.
    found = False
    config_list = mt.config.get("search-binsearch/downloaded/nzb")
    for item in config_list:
        if ( item["id"] == str(query_id) ): found = True
    
    if ( not found ):
        element = mt.config.ConfigItem("")
        element["id"] = str(query_id)
        mt.config.add(element, "search-binsearch/downloaded/nzb", "packages/search-binsearch/downloaded.cfg")
        mt.config.save("packages/search-binsearch/downloaded.cfg")

    return True

