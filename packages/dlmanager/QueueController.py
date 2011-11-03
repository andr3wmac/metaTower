import mtCore as mt
import threading, os, mtMisc, commands, shutil
from NZB.NZBClient import NZBClient, time

class QueueController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self.queue_folder = "packages/dlmanager/queue"

        self.torrent_queue = []
        self.torrent_engine = None
        self.nzb_queue = []
        self.nzb_engine = None
    
        self.torrent_enabled = False

        self.running = True
        self.last_update = 0

        # load any queue data that could be left from the last run.
        config = mt.config
        config.load("packages/dlmanager/dlmanager.xml")

        for item in config.get("dlmanager/queue/nzb"):
            if ( not os.path.isfile(item["filename"]) ): continue 
            nzb = self.NZBQueueItem()
            nzb.uid = item["uid"]
            nzb.filename = item["filename"]
            nzb.completed = bool(int(item["completed"]))
            nzb.error = bool(int(item["error"]))
            nzb.par2_results = item["par2_results"]
            nzb.unrar_results = item["unrar_results"]
            nzb.save_to = item["save_to"]
            self.nzb_queue.append(nzb)

        if ( False ):
            for item in config.get("dlmanager/queue/torrent"):
                if ( not os.path.isfile(item["filename"]) ): continue 
                torrent = self.TorrentQueueItem()
                torrent.uid = item["uid"]
                torrent.filename = item["filename"]
                torrent.completed = bool(int(item["completed"]))
                torrent.error = bool(int(item["error"]))
                torrent.save_to = item["save_to"]
                torrent_queue.append(torrent)
            self.torrent_engine = lt.session()
            self.torrent_engine.listen_on(6881, 6891)


    def removeItems(self, items):
        for nzb in self.nzb_queue:
            if ( nzb.uid in items ):
                if ( nzb.downloading ):
                    if ( self.nzb_engine != None ):
                        self.nzb_engine.stopDownload()
                        self.nzb_engine = None
                os.remove(nzb.filename)
                nzb.removed = True

        for torrent in self.torrent_queue:
            if torrent.uid in items:
                if ( torrent.lt_entry != None ):
                    self.torrent_engine.remove_torrent(torrent.lt_entry)
                    torrent.lt_entry = None
                os.remove(torrent.filename)
                torrent.removed = True

    class NZBQueueItem():
        removed = False
        filename = ""
        save_to = ""
        completed = False
        error = False
        downloading = False
        par2_results = "Checking and repairing files.."
        unrar_results = ""
        last_update = 0
        uid = ""
    
    class TorrentQueueItem():
        removed = False
        filename = ""
        save_to = ""
        completed = False
        error = False
        downloading = False
        last_update = 0
        lt_entry = None
        uid = ""
    
    def torrentFiles(self):
        results = []
        for f in os.listdir(self.queue_folder):
            ff = os.path.join(self.queue_folder, f)
            if os.path.isfile(ff):
                if ( f.endswith(".torrent") ): results.append(ff)
        return results

    def nzbFiles(self):
        results = []
        for f in os.listdir(self.queue_folder):
            ff = os.path.join(self.queue_folder, f)
            if os.path.isfile(ff):
                if ( f.endswith(".nzb") ): results.append(ff)
        return results

    def torrentUpdate(self):
        for torrent in self.torrent_queue:
            if ( torrent.lt_entry == None ):
                try:
                    info = lt.torrent_info(torrent.filename)
                    torrent.lt_entry = self.torrent_engine.add_torrent({'ti': info, 'save_path': torrent.save_to})
                except:
                    mt.log.error("Could not add torrent.")
                    pass

    def nzbUpdate(self):
        # evaluate the state of the NZB Queue.
        if ( self.nzb_engine == None ):
            for queue_item in self.nzb_queue:
                if ( not queue_item.downloading ) and ( not queue_item.completed ):
                    queue_item.downloading = True
    
                    ssl = mt.config["dlmanager/nzb"]["ssl"]
                    ssl_enabled = ((ssl.lower()=="true")or(ssl=="1")or(ssl.lower()=="yes"))

                    self.nzb_engine = NZBClient(
                        nzbFile=queue_item.filename, 
                        save_to=queue_item.save_to, 
                        nntpServer=mt.config["dlmanager/nzb"]["server"], 
                        nntpPort=int(mt.config["dlmanager/nzb"]["port"]), 
                        nntpConnections=int(mt.config["dlmanager/nzb"]["connections"]), 
                        nntpUser=mt.config["dlmanager/nzb"]["username"], 
                        nntpPassword=mt.config["dlmanager/nzb"]["password"], 
                        nntpSSL=ssl_enabled)
                    self.nzb_engine.start()
                    break
        else:
            status = self.nzb_engine.status
            if ( status.completed ) or ( status.error_occured ):
                for queue_item in self.nzb_queue:
                    if ( queue_item.filename == status.file_name ):
                        queue_item.completed = status.completed
                        queue_item.error = status.error_occured
                        queue_item.downloading = False
                        self.nzb_engine.stopDownload()
                        self.nzb_engine = None
                        if ( queue_item.completed ) and ( not queue_item.error ): self.nzbComplete(queue_item)

    def nzbComplete(self, queue_item):
        # attempt to par2.
        par2_result = self.par2Folder(queue_item.save_to)
        if ( par2_result == False ): queue_item.par2_results = "No par2 files found."
        else: queue_item.par2_results = par2_result

        # attempt to unrar.
        queue_item.unrar_results = "Decompressing files.."
        unrar_result = self.unrarFolder(queue_item.save_to)
        if ( unrar_result == False ): queue_item.unrar_results = "No rar files found."
        else: queue_item.unrar_results = unrar_result

    def unrarFolder(self, path):
        result = False
        folders = []
        for f in os.listdir(path):
            if ( result != False ): break

            ff = os.path.join(path, f)
            if ( os.path.isfile(ff) and f.endswith(".rar") ):
                rar_file = ff.replace(" ", "\ ").replace("(", "\(").replace(")", "\)")
                try:
                    output = commands.getoutput('unrar e -o+ ' + rar_file + " " + mt.config["dlmanager/nzb"]["save_to"])
                    output_args = output.splitlines()
                    result = output_args[len(output_args)-1]
                except:
                    mt.log.error("Unrar error.")
            if ( os.path.isdir(ff) ): folders.append(ff)
        if ( result == False ):
            for f in folders: result = self.unrarFolder(f)
        return result
        
    def par2Folder(self, path):
        result = False
        folders = []
        for f in os.listdir(path):
            if ( result != False ): break

            ff = os.path.join(path, f)
            if ( os.path.isfile(ff) and f.endswith(".par2") ): 
                par2_file = ff.replace(" ", "\ ").replace("(", "\(").replace(")", "\)")
                try:
                    output = commands.getoutput('par2 r ' + par2_file)
                    output_args = output.splitlines()
                    result = output_args[len(output_args)-1]
                except:
                    mt.log.error("Par2 error.")
            if ( os.path.isdir(ff) ): folders.append(ff)
        if ( result == False ):
            for f in folders: result = self.par2Folder(f)
        return result

    def run(self):
        try:
            while ( self.running ):
                if ( time.time() - self.last_update > 5 ):
                    for nzb in self.nzbFiles():
                        already_queued = False
                        for queue_item in self.nzb_queue:
                            if (( queue_item.filename.endswith(nzb) ) and ( queue_item.removed == False )): already_queued = True
                        if ( not already_queued ):
                            new_item = self.NZBQueueItem()
                            new_item.filename = nzb
                            new_item.uid = mtMisc.uid()
                            new_item.save_to = os.path.join(mt.config["dlmanager/nzb"]["save_to"], os.path.basename(nzb).replace(".nzb", "")) + "/"
                            self.nzb_queue.append(new_item)
                    self.nzbUpdate()

                    if ( self.torrent_enabled ):
                        for torrent in self.torrentFiles():
                            already_queued = False
                            for queue_item in torrent_queue:
                                if (( queue_item.filename.endswith(torrent) ) and ( queue_item.removed == False )): already_queued = True
                            if ( not already_queued ):
                                new_item = self.TorrentQueueItem()
                                new_item.filename = torrent
                                new_item.uid = mtMisc.uid()
                                new_item.save_to = os.path.join(mt.config["dlmanager/torrent"]["dir"], os.path.basename(torrent)) + "/"
                                self.torrent_queue.append(new_item)
                        self.torrentUpdate()
                    
                    self.last_update = time.time()
                time.sleep(1)  
        finally:
            self.shutdown() 

    def shutdown(self):
        config = mt.config
        config.clear("dlmanager/queue")

        for item in self.nzb_queue:
            if ( item.removed ): continue
            element = config.ConfigItem("")
            element["uid"] = item.uid
            element["filename"] = item.filename
            element["completed"] = str(int(item.completed))
            element["error"] = str(int(item.error))
            element["par2_results"] = item.par2_results
            element["unrar_results"] = item.unrar_results
            element["save_to"] = item.save_to
            config.add(element, "dlmanager/queue/nzb", "packages/dlmanager/dlmanager.xml")

        for item in self.torrent_queue:
            if ( item.removed ): continue
            element = config.ConfigItem("")
            element["uid"] = item.uid
            element["filename"] = item.filename
            element["completed"] = str(int(item.completed))
            element["error"] = str(int(item.error))
            element["save_to"] = item.save_to
            config.add(element, "dlmanager/queue/torrent", "packages/dlmanager/dlmanager.xml")

        if ( self.nzb_engine != None ):
            self.nzb_engine.stopDownload()
        
        if ( self.torrent_engine != None ):
            del self.torrent_engine

        self.running = False