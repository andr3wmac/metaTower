import os, commands, shutil, mt, time, PostProcessor
from NZB.NZBClient import NZBClient
from mt import threads

libtorrent_enabled = False
try:
    import libtorrent as lt
    libtorrent_enabled = True
except:
    pass

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
        downloading_magnet = False

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
            mt.log.warning("Usenet downloading disabled, no configuration found.")

        if ( libtorrent_enabled ):
            self.torrent_enabled = ( config["dlmanager/torrent/save_to"] != "" )
            if ( not self.torrent_enabled ):
                mt.log.warning("Torrent downloading disabled, no configuration found.")
        else:
            mt.log.warning("Torrent downloading disabled, python-libtorrent not found.")
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

    def remove(self, uid, delete):
        for nzb in self.nzb_queue:
            if ( nzb.uid == uid ):
                if ( nzb.downloading ):
                    if ( self.nzb_engine != None ):
                        self.nzb_engine.stop()
                        self.nzb_engine = None
                os.remove(nzb.filename)
                mt.utils.rmdir(nzb.save_to)
                nzb.removed = True

        for torrent in self.torrent_queue:
            if torrent.uid == uid:
                if ( torrent.lt_entry != None ):
                    self.torrent_engine.remove_torrent(torrent.lt_entry)
                    torrent.lt_entry = None
                os.remove(torrent.filename)
                if ( delete ):
                    mt.utils.rmdir(torrent.save_to)
                torrent.removed = True

    def removeCompleted(self):
        for nzb in self.nzb_queue:
            if ( not nzb.downloading ) and ( nzb.completed or nzb.error ):
                os.remove(nzb.filename)
                mt.utils.rmdir(nzb.save_to, False)
                nzb.removed = True
    
    def torrentFiles(self):
        results = []
        for f in os.listdir(self.queue_folder):
            ff = os.path.join(self.queue_folder, f)
            if os.path.isfile(ff):
                if ( f.endswith(".torrent") ): results.append(ff)
                if ( f.endswith(".magnet") ): results.append(ff)
        return results

    def nzbFiles(self):
        results = []
        for f in os.listdir(self.queue_folder):
            ff = os.path.join(self.queue_folder, f)
            if os.path.isfile(ff):
                if ( f.endswith(".nzb") ): results.append(ff)
        return results

    def startMagnet(self, torrent):
        if ( not os.path.isfile(torrent.filename) ): return None
        f = open(torrent.filename)
        magnet = f.read()
        f.close()
        parms = {
            'url': magnet,
            'save_path': torrent.save_to,
            'duplicate_is_error': True,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True
        }
        return lt.add_magnet_uri(self.torrent_engine, magnet, parms)

    def torrentUpdate(self):
        # exit if disabled
        if ( not self.torrent_enabled ): return

        for torrent in self.torrent_queue:
            if ( torrent.removed or torrent.completed ): continue
            try:
                info = None
                
                # process torrent.
                if ( torrent.lt_entry == None ):    
                    if torrent.filename.lower().endswith(".magnet"):
                        torrent.lt_entry = self.startMagnet(torrent)
                    else:
                        info = lt.torrent_info(torrent.filename)
                        torrent.lt_entry = self.torrent_engine.add_torrent({'ti': info, 'save_path': torrent.save_to})

                else:
                    status = torrent.lt_entry.status()
                    if ( int(status.state) == 5 ):
                        self.torrent_engine.remove_torrent(torrent.lt_entry)
                        torrent.lt_entry = None
                        torrent.completed = True

            except:
                mt.log.error("Could not add torrent: " + torrent.filename)
                pass

    def nzbUpdate(self):
        if ( not self.nzb_enabled ): return

        # evaluate the state of the NZB Queue.
        if ( self.nzb_engine == None ):
            for queue_item in self.nzb_queue:
                if ( not queue_item.downloading ) and ( not queue_item.completed ) and ( not queue_item.error ):
                    if ( not os.path.isfile(queue_item.filename) ): continue                    
                    try:
                        queue_item.downloading = True

                        ssl = mt.config["dlmanager/nzb/ssl"]
                        ssl_enabled = ssl.isTrue()

                        self.nzb_engine = threads.Process(NZBClient,
                            nzbFile =           queue_item.filename, 
                            save_to =           queue_item.save_to, 
                            nntpServer =        mt.config["dlmanager/nzb/server"], 
                            nntpPort=           int(mt.config["dlmanager/nzb/port"]), 
                            nntpConnections =   int(mt.config["dlmanager/nzb/connections"]), 
                            nntpUser =          mt.config["dlmanager/nzb/username"], 
                            nntpPassword =      mt.config["dlmanager/nzb/password"], 
                            nntpSSL =           ssl_enabled,
                            cache_path =        mt.config["dlmanager/nzb/cache_path"])
                        self.nzb_engine.start()

                        break

                    except:
                        queue_item.downloading = False
                        queue_item.error = True
                        self.nzb_engine = None
                        pass
                        
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
        PostProcessor.process_nzb(queue_item)

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
                        save_folder = os.path.splitext(os.path.basename(nzb))[0]
                        new_item.save_to = os.path.join(mt.config["dlmanager/nzb/save_to"], save_folder) + ".download/"
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
                        save_folder = os.path.splitext(os.path.basename(torrent))[0]
                        new_item.save_to = os.path.join(mt.config["dlmanager/torrent/save_to"], save_folder) + ".download/"
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
            if ( self.torrent_engine ): self.torrent_engine.pause()
            del self.torrent_engine
