import sys, os, urllib, time, socket, mt, ssl
from dlmanager.NZB import NZBParser
from dlmanager.NZB.nntplib2 import NNTP_SSL,NNTPError,NNTP, NNTPReplyError
from dlmanager.NZB.Decoder import ArticleDecoder

class StatusReport(object):
    def __init__(self):
        self.message = "Downloading.."
        self.total_bytes = 0
        self.current_bytes = 0
        self.completed = False
        self.error_occured = False
        self.start_time = 0
        self.file_name = ""
        self.kbps = 0
        self.assembly = False
        self.assembly_percent = 0

class NZBClient():
    def __init__(self, nzbFile, save_to, nntpServer, nntpPort, nntpUser=None, nntpPassword=None, nntpSSL=False, nntpConnections=5, cache_path=""):

        # Settings
        self.save_to = save_to
        self.nntpServer = nntpServer
        self.nntpUser = nntpUser
        self.nntpPort = nntpPort
        self.nntpPassword = nntpPassword
        self.nntpSSL = nntpSSL
        self.nntpConnections = nntpConnections
        self.threads = []
        self.running = False

        # setup our cache folder.
        self.cache_path = cache_path
        if ( self.cache_path == "" ): self.cache_path = "packages/dlmanager/cache/"
        self.clearCache()

        # ensure both directorys exist
        mt.utils.mkdir(self.save_to)
        mt.utils.mkdir(self.cache_path)

        # Open the NZB, get this show started.
        realFile = urllib.urlopen(nzbFile)
        self.nzb = NZBParser.parse(realFile)
        self.all_decoded = False
        self.connection_count = 0

        # used to track status.
        self.status = StatusReport()
        self.status.file_name = nzbFile
        self.status.total_bytes = self.nzb.size

        # Segment tracking.
        self.cache = []
        self.segment_list = []
        self.segments_finished = []
        self.segments_aborted = []

        # Queues.
        self.segment_queue = []
        self.failed_queue = []

        # Used to track the speed.
        self.speedTime = 0
        self.speedCounter = 0

    def start(self):
        # keep track of running time.
        self.status.start_time = time.time()
        self.running = True

        # Generate a list of segments and build our queue.
        for file in self.nzb.files:
            for seg in file.segments:
                self.segment_list.append(seg.msgid)
                self.segment_queue.append(seg)

        # start the connections.
        for a in range(0, self.nntpConnections):
            thread = NNTPConnection(a, 
                self.nntpServer, 
                self.nntpPort, 
                self.nntpUser, 
                self.nntpPassword, 
                self.nntpSSL, 
                self.nextSeg, 
                self.segComplete, 
                self.segFailed, 
                self.threadStopped)
            self.threads.append(thread)
            self.connection_count += 1
            thread.start()

        # start the article decoder.
        self.articleDecoder = ArticleDecoder(self.decodeNextSeg, 
                self.save_to, 
                self.cache_path, 
                self.decodeFinished, 
                self.decodeSuccess, 
                self.decodeFailed,
                self.assemblyStatus)
        self.articleDecoder.start()

    def getStatus(self):
        return self.status

    # Article Decoder - Next segment.
    def decodeNextSeg(self):
        # if we're not running send an instant kill switch.
        if ( not self.running ): return -1

        # try to grab a segment from the cache to decode.
        seg = None
        try:
            seg = self.cache.pop()
        except:
            pass	

        if ( seg == None ) and ( self.all_decoded ):
            return -1
        return seg

    # Article Decoder - Decoded all segments.
    def decodeFinished(self):
        self.status.completed = True
        
    # Article Decoder - Decode success.
    def decodeSuccess(self, seg):
        self.status.current_bytes += seg.size
        self.segments_finished.append(seg.msgid)
        if ( (len(self.segments_finished)+len(self.segments_aborted)) >= len(self.segment_list) ):
            self.all_decoded = True

    # Article Decoder - Decode failed.
    def decodeFailed(self, seg):
        if ( seg == None ): return
        mt.log.debug("Segment failed to decode: " + seg.msgid)
        self.segFailed(seg)

    # Article Decoder - Assembly Status.
    def assemblyStatus(self, percent):
        self.status.assembly = True
        self.status.assembly_percent = percent

    # NNTP Connection - Thread stopped.
    def threadStopped(self, thread_num):
        self.connection_count -= 1

    # NNTP Connection - Segment completed.
    def segComplete(self, seg):
        if ( seg == None ): return

        if ( seg.data ): 
            data_size = len("".join(seg.data))

            current_time = time.time()
            if ( (current_time - self.speedTime) > 1 ):
                self.status.kbps = self.speedCounter
                self.speedCounter = 0
                self.speedTime = current_time
            else:
                self.speedCounter += (data_size/1024)

            self.cache.append(seg)
        #mt.log.debug("Segment Complete: " + seg.msgid)

    # NNTP Connection - Download of segment failed.
    def segFailed(self, seg):
        if ( seg == None ): return

        if ( seg.aborted() ):
            mt.log.error("Segment Aborted: " + seg.msgid + " after " + str(seg.retries) + " attempts.")
            self.segments_aborted.append(seg.msgid)
            seg.data = []
            if ( (len(self.segments_finished)+len(self.segments_aborted)) >= len(self.segment_list) ):
                self.all_decoded = True
            return

        seg.retries += 1

        mt.log.error("Segment Failed: " + seg.msgid + " Attempt #" + str(seg.retries) + ".")
        self.failed_queue.append(seg)

    # NNTP Connection - Next Segment
    def nextSeg(self):
        # if we're not running send an instant kill switch.
        if ( not self.running ): return -1

        # try to get a segment from main queue or failed queue.
        queue_empty = False
        seg = None
        try:
            seg = self.segment_queue.pop()
        except:
            try:
                seg = self.failed_queue.pop()
            except:
                queue_empty = True
                pass
            pass

        # We're all outta segments, if they're done decoding, kill the threads.
        if ( queue_empty ) and ( self.all_decoded ):
            return -1

        return seg

    # empty the cache of any files.
    def clearCache(self):
        mt.utils.rmdir(self.cache_path)
            
    def stop(self):
        self.running = False
        self.articleDecoder.stop()
        for thread in self.threads:
            thread.stop()
        self.clearCache()

class NNTPConnection(mt.threads.Thread):
    def __init__(self, connection_number, server, port, username, password, ssl, nextSegFunc, onSegComplete = None, onSegFailed = None, onThreadStop = None):
        mt.threads.Thread.__init__(self)

        # Settings
        self.connection = None
        self.connection_number = connection_number
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.ssl = ssl

        # Events.
        self.nextSegFunc = nextSegFunc
        self.onSegComplete = onSegComplete
        self.onSegFailed = onSegFailed
        self.onThreadStop = onThreadStop

    def connect(self):
        # Open either an SSL or regular NNTP connection.
        try:
            if ( self.ssl ):
                self.connection = NNTP_SSL(self.server, self.port, self.username, self.password, False, True, timeout=15)
            else:
                self.connection = NNTP(self.server, self.port, self.username, self.password, False, True, timeout=15)
        except:
            pass

        if ( self.connection ): return True
        return False

    def disconnect(self):
        if ( self.connection ):
            try:
                self.connection.quit()
            except:
                pass
        self.connection = None

    def run(self):
        connection = None
        seg = None

        # Thread has started.
        mt.log.debug("Thread " + str(self.connection_number) + " started.")
        start_time = time.time()

        while(self.running):
            seg = None
            connected = self.connect()
            if ( connected ):
                while(self.running):
                    seg = self.nextSegFunc()
                    
                    # Out of segments, sleep for a bit and see if we get anymore.
                    if ( seg == None ):
                        self.sleep(0.1)
                        continue

                    # Download complete, bail.
                    if ( seg == -1 ): 
                        self.running = False
                        seg = None
                        break

                    # Attempt to grab a segment.
                    try:
                        resp, nr, id, data = self.connection.body("<%s>" % seg.msgid)
                        if resp[0] == "2":
                            seg.data = data
                            if ( self.onSegComplete ): self.onSegComplete(seg)
                            seg = None

                    except ssl.SSLError:
                        break
                         
                    except NNTPError as e:
                        mt.log.error("Error getting segment: " + e.response)
                        pass
   
                    except:
                        mt.log.error("Error getting segment.")
                        pass

                    if ( seg and self.onSegFailed ): 
                        self.onSegFailed(seg)
                        seg = None

                # Disconnect when we're finished.
                if ( seg and self.onSegFailed ): self.onSegFailed(seg)
                self.disconnect()
            else:
                mt.log.error("Connection error. Reconnecting in 3 seconds.")
                self.sleep(3)

        # Thread has ended.
        self.disconnect() # just to be safe.
        end_time = time.time()
        mt.log.debug("Thread " + str(self.connection_number) + " stopped after " + str(end_time-start_time) + " seconds.")
        if ( self.onThreadStop ): self.onThreadStop(self.connection_number)
