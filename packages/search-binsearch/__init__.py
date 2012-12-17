import mt, os, urllib

save_to = ""

def onLoad():
    global save_to

    cfg = mt.config
    cfg.load("packages/search-binsearch/settings.cfg")
    cfg.load("packages/search-binsearch/downloaded.cfg", True)

    save_to = cfg["search-binsearch/save_to"]

    if mt.packages.search:
        mt.packages.search.addEngine("binsearch.info", search, save)

def search(query):
    global last_search
    last_search = query

    query_string = urllib.urlencode({"q": query, "max": "50"})        
    url = "http://binsearch.info/?" + query_string
    data = mt.utils.openURL(url)

    result_list = []
    data = data.split("<td><input type=\"checkbox\" name=\"")

    dlist = []
    config_list = mt.config.get("search-binsearch/downloaded/nzb")
    for item in config_list:
        dlist.append(item["id"])

    if ( len(data) > 3 ):
        data = data[2:-1]
        for raw_nzb in data:
            raw_nzb = raw_nzb.split("\" ><td><span class=\"s\">")
            
            result = {}
            result["id"] = int(raw_nzb[0])
            result["name"] = raw_nzb[1].split("</span>")[0]

            # try for size
            a = raw_nzb[1].split("size: ")
            if ( len(a) > 1 ):
                result["size"] = a[1].split(", parts")[0].replace("&nbsp;", " ")

            result["downloaded"] = str(result["id"]) in dlist

            result_list.append(result)

    return result_list

def save(query_id):
    global save_to, last_search

    url = "http://binsearch.info/fcgi/nzb.fcgi"
    post_data = str(query_id) + "=on&action=nzb"    
    data = mt.utils.openURL(url, post_data)

    f = open(os.path.join(save_to, last_search + ".nzb"), "w")
    f.write(data)
    f.close()

    # generate a list of files from the known library
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

