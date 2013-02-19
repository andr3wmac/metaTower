import os, commands, shutil, mt, time
from mt import threads

import FileDownloader, InfoExtractors

class QueueController(threads.Thread):
    class YoutubeQueueItem():
        removed = False
        url = ""
        save_to = ""
        title = ""
        flv_path = ""
        state = 0
        progress = 0
        last_update = 0
        uid = 0

    def __init__(self):
        # init thread with a 5 second tick interval.
        threads.Thread.__init__(self, 5)

        self.youtube_enabled = True
        self.youtube_queue = []
        self.youtube_engine = None
        self.youtube_dl = None

        self.last_update = 0

    def add(self, url):
        yt = self.YoutubeQueueItem()
        yt.uid = mt.utils.uid()
        yt.url = url
        yt.title = url
        yt.save_to = "files/%(title)s.flv"
        self.youtube_queue.append(yt)

    def remove(self, uid):
        for yt in self.youtube_queue:
            if yt.uid == uid: yt.removed = True

    def removeCompleted(self):
        for yt in self.youtube_queue:
            if ( yt.state == 3 ): yt.removed = True

    def ytConvertProgress(self, filename, progress):
        self.youtube_dl.progress = progress
        if ( progress > 100 ):
            mt.utils.rmdir(self.youtube_dl.save_to)
            self.youtube_dl.progress = 100
            self.youtube_dl.state = 3
            self.youtube_engine = None

    def youtubeProgress(self, info):
        if ( info["status"] == "downloading" ):
            self.youtube_dl.state = 1
            self.youtube_dl.save_to = info["filename"]
            self.youtube_dl.progress = int(float(info["downloaded_bytes"])/float(info["total_bytes"])*100)
            self.youtube_dl.title = info["filename"].replace("files/", "").replace(".flv", "")

        if ( info["status"] == "finished" ):
            if ( mt.packages.isLoaded("ffmpeg") ):
                ffmpeg = mt.packages.ffmpeg
                ffmpeg.convertToMP3(info["filename"], self.ytConvertProgress)
                self.youtube_dl.state = 2
                self.youtube_dl.progress = 0
            else:
                self.youtube_dl.state = 3
                self.youtube_dl.progress = 100

    def youtubeUpdate(self):
        # exit if disabled
        if ( not self.youtube_enabled ): return

        for yt in self.youtube_queue:
            if ( yt.removed ): continue
            if ( yt.state > 0 ): continue

            if ( self.youtube_engine == None ):
                self.youtube_engine = FileDownloader.FileDownloader({"quiet": True, "outtmpl": yt.save_to})
                self.youtube_engine.add_progress_hook(self.youtubeProgress)
                extractors = InfoExtractors.gen_extractors()
                for extractor in extractors:
                    self.youtube_engine.add_info_extractor(extractor)

                self.youtube_dl = yt
                self.youtube_engine.download([yt.url])
                

    def tick(self):
        try:
            if ( self.youtube_enabled ):
                self.youtubeUpdate()

        except Exception as inst:
            mt.log.error("Queue Error: " + str(inst.args))

    def stop(self):
        threads.Thread.stop(self)
        
        if ( hasattr(self, "youtube_engine") ):
            if ( self.youtube_engine ): self.youtube_engine.stop()
            del self.youtube_engine
