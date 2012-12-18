import mt, os, urllib

torrent_list = []
save_to = ""

class TorrentResult:
    def __init__(self, query_id, name, magnet_link):
        self.query_id = query_id
        self.magnet_link = magnet_link
        self.name = name

def onLoad():
    global save_to

    cfg = mt.config
    cfg.load("packages/search-piratebay/search-piratebay.cfg")
    cfg.load("packages/search-piratebay/downloaded.cfg", True)
    save_to = cfg["search-piratebay/save_to"]

    if mt.packages.search:
        mt.packages.search.addEngine("thepiratebay.se", query, save)

def query(content):
    global torrent_list
    torrent_list = []    
    result_list = []
    dlist = []
    
    # load the list of previously downloaded torrents.
    config_list = mt.config.get("search-piratebay/downloaded/torrent")
    for item in config_list:
        dlist.append(item["id"])

    # query the pirate bay.
    query_string = urllib.urlencode({"": content})[1:]  
    data = mt.utils.openURL('http://thepiratebay.se/search/' + query_string + '/0/99/0')    
    data = data.split("<div class=\"detName\">")
    if ( len(data) > 3 ):
        data = data[2:-1]
        for raw_data in data:
            # process data
            torrent_data = raw_data.split("\">")
            name = torrent_data[1].split("</a>")[0]           
            magnet = torrent_data[1].split("<a href=\"")[1].split("\" title=\"")[0]     
            torrent_id = mt.utils.md5(magnet)        

            # attempt to get size
            size = "0 MiB"
            size_data = raw_data.split("Size ")
            if len(size_data) > 1:
                size = size_data[1].split(", UL")[0].replace("&nbsp;", " ") 

            # store torrent for later
            new_torrent = TorrentResult(torrent_id, name, magnet)
            torrent_list.append(new_torrent)
    
            # generate result for display.
            result = {}
            result["id"] = torrent_id
            result["name"] = name
            result["size"] = size
            result["downloaded"] = str(result["id"]) in dlist
            result_list.append(result)

    return result_list

def save(query_id):
    global save_to, torrent_list    

    torrent = None
    for t in torrent_list:
        if (t.query_id == query_id): torrent = t
    if ( torrent == None ): return False

    f = open(os.path.join(save_to, torrent.name + ".magnet"), "w")
    f.write(torrent.magnet_link)
    f.close()

    # generate a list of files from the known library
    found = False
    config_list = mt.config.get("search-piratebay/downloaded/torrent")
    for item in config_list:
        if ( item["id"] == str(query_id) ): found = True
    
    if ( not found ):
        element = mt.config.ConfigItem("")
        element["id"] = str(query_id)
        mt.config.add(element, "search-piratebay/downloaded/torrent", "packages/search-piratebay/downloaded.cfg")
        mt.config.save("packages/search-piratebay/downloaded.cfg")

    return True
