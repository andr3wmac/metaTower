import os, commands, shutil, mt, time
from NZB.NZBClient import NZBClient
from NZB import Extractor
from mt import threads

libtorrent_enabled = False
try:
    import libtorrent as lt
    libtorrent_enabled = True
except:
    mt.log.error("libtorrent import failed. If you're using linux install the package 'python-libtorrent'. If you're on windows ensure libtorrent.pyd is present in the dlmanager directory.")

class QueueController(threads.Thread):
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
        realFilename = None
        save_to = ""
        completed = False
        error = False
        downloading = False
        last_update = 0
        uid = ""

        lt_entry = None

    def __init__(self):
        global libtorrent_enabled

        # init thread with a 5 second tick interval.
        threads.Thread.__init__(self, 5)

        self.queue_folder = "packages/dlmanager/queue"
        mt.utils.mkdir(self.queue_folder)

        self.torrent_queue = []
        self.torrent_engine = None
        self.nzb_queue = []
        self.nzb_engine = None
        self.last_update = 0

        # load any queue data that could be left from the last run.
        config = mt.config
        self.nzb_enabled = ( config["dlmanager/nzb/server"] != "" )
        if ( not self.nzb_enabled ):
            mt.log.info("NZB downloader disabled, no configuration found.")

        if ( libtorrent_enabled ):
            self.torrent_enabled = ( config["dlmanager/torrent/save_to"] != "" )
            if ( not self.torrent_enabled ):
                mt.log.info("Torrent downloader disabled, no configuration found.")
        else:
            self.torrent_enabled = False

        if ( self.nzb_enabled ):
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
            
        if ( self.torrent_enabled ):
            for item in config.get("dlmanager/queue/torrent"):
                if ( not os.path.isfile(item["filename"]) ): continue 
                torrent = self.TorrentQueueItem()
                torrent.uid = item["uid"]
                torrent.filename = item["filename"]
                torrent.completed = bool(int(item["completed"]))
                torrent.error = bool(int(item["error"]))
                torrent.save_to = item["save_to"]
                self.torrent_queue.append(torrent)
            self.torrent_engine = lt.session()
            self.torrent_engine.listen_on(6881, 6891)

    def removeItems(self, items):
        for nzb in self.nzb_queue:
            if ( nzb.uid in items ):
                if ( nzb.downloading ):
                    if ( self.nzb_engine != None ):
                        self.nzb_engine.stop()
                        self.nzb_engine = None
                os.remove(nzb.filename)
                mt.utils.rmdir(nzb.save_to)
                nzb.removed = True

        for torrent in self.torrent_queue:
            if torrent.uid in items:
                if ( torrent.lt_entry != None ):
                    self.torrent_engine.remove_torrent(torrent.lt_entry)
                    torrent.lt_entry = None
                os.remove(torrent.filename)
                torrent.removed = True
    
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
        if ( not self.torrent_enabled ): return

        for torrent in self.torrent_queue:
            if ( torrent.lt_entry == None ) and ( not torrent.removed ):
                try:
                    info = lt.torrent_info(torrent.filename)
                    torrent.lt_entry = self.torrent_engine.add_torrent({'ti': info, 'save_path': torrent.save_to})
                except:
                    mt.log.error("Could not add torrent.")
                    pass

    def nzbUpdate(self):
        if ( not self.nzb_enabled ): return

        # evaluate the state of the NZB Queue.
        if ( self.nzb_engine == None ):
            for queue_item in self.nzb_queue:
                if ( not queue_item.downloading ) and ( not queue_item.completed ) and ( not queue_item.error ):
                    #try:
                    queue_item.downloading = True

                    ssl = mt.config["dlmanager/nzb/ssl"]
                    ssl_enabled = ssl.isTrue()

                    self.nzb_engine = threads.Process(NZBClient,
                        nzbFile=queue_item.filename, 
                        save_to=queue_item.save_to, 
                        nntpServer=mt.config["dlmanager/nzb/server"], 
                        nntpPort=int(mt.config["dlmanager/nzb/port"]), 
                        nntpConnections=int(mt.config["dlmanager/nzb/connections"]), 
                        nntpUser=mt.config["dlmanager/nzb/username"], 
                        nntpPassword=mt.config["dlmanager/nzb/password"], 
                        nntpSSL=ssl_enabled,
                        cache_path=mt.config["dlmanager/nzb/cache_path"])
                    self.nzb_engine.start()
                    break
                    #except:
                    #    queue_item.downloading = False
                    #    queue_item.error = True
                    #    self.nzb_engine = None
                        
        else:
            status = self.nzb_engine.execute("getStatus")
            if ( status.completed ) or ( status.error_occured ):
                for queue_item in self.nzb_queue:
                    if ( queue_item.filename == status.file_name ):
                        queue_item.completed = status.completed
                        queue_item.error = status.error_occured
                        queue_item.downloading = False
                        if ( self.nzb_engine != None ):                        
                            self.nzb_engine.stop()
                            self.nzb_engine = None
                        if ( queue_item.completed ) and ( not queue_item.error ): self.nzbComplete(queue_item)

    def nzbComplete(self, queue_item):
        # attempt to par2.
        par2_result = Extractor.par2Folder(queue_item.save_to)
        if ( par2_result == False ): queue_item.par2_results = "No par2 files found."
        else: queue_item.par2_results = par2_result

        # attempt to unrar.
        queue_item.unrar_results = "Decompressing files.."
        unrar_result = Extractor.unrarFolder(queue_item.save_to)
        if ( unrar_result == False ): queue_item.unrar_results = "No rar files found."
        else: queue_item.unrar_results = unrar_result

    def tick(self):
        try:
            if ( self.nzb_enabled ):
                for nzb in self.nzbFiles():
                    already_queued = False
                    for queue_item in self.nzb_queue:
                        if (( queue_item.filename.endswith(nzb) ) and ( queue_item.removed == False )): already_queued = True
                    if ( not already_queued ):
                        new_item = self.NZBQueueItem()
                        new_item.filename = nzb
                        new_item.uid = mt.utils.uid()
                        new_item.save_to = os.path.join(mt.config["dlmanager/nzb/save_to"], os.path.basename(nzb).replace(".nzb", "")) + "/"
                        self.nzb_queue.append(new_item)
                self.nzbUpdate()
            
            if ( self.torrent_enabled ):
                for torrent in self.torrentFiles():
                    already_queued = False
                    for queue_item in self.torrent_queue:
                        if (( queue_item.filename.endswith(torrent) ) and ( queue_item.removed == False )): already_queued = True
                    if ( not already_queued ):
                        new_item = self.TorrentQueueItem()
                        new_item.filename = torrent
                        new_item.uid = mt.utils.uid()
                        new_item.save_to = os.path.join(mt.config["dlmanager/torrent/save_to"], os.path.basename(torrent)) + "/"
                        self.torrent_queue.append(new_item)
                self.torrentUpdate()
        except Exception as inst:
            mt.log.error("Queue Error: " + str(inst.args))

    def stop(self):
        threads.Thread.stop(self)

        if ( hasattr(self, "nzb_engine") ):
            if ( self.nzb_engine ): self.nzb_engine.stop()
            del self.nzb_engine
        
        if ( hasattr(self, "torrent_engine") ):
            del self.torrent_engine
