import sys, os, urllib, time, socket
import mtCore as mt
import mtMisc
from threading import Thread, Lock
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

        # setup our cache folder.
        self.cache_path = cache_path
        if ( self.cache_path == "" ): self.cache_path = "packages/dlmanager/cache/"
        self.clearCache()

        # ensure both directorys exist
        mtMisc.mkdir(self.save_to)
        mtMisc.mkdir(self.cache_path)

        # Open the NZB, get this show started.
        realFile = urllib.urlopen(nzbFile)
        self.nzb = NZBParser.parse(realFile)
        self.running = True
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

        # Generate a list of segments and build our queue.
        for file in self.nzb.files:
            for seg in file.segments:
                # we don't need any duplicates.
                if ( not seg.msgid in self.segment_list ): 
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
            thread.start()
            self.connection_count += 1

        # start the article decoder.
        self.articleDecoder = ArticleDecoder(self.decodeNextSeg, 
                self.save_to, 
                self.cache_path, 
                self.decodeFinished, 
                self.decodeSuccess, 
                self.decodeFailed)
        self.articleDecoder.start()

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

    # NNTP Connection - Thread stopped.
    def threadStopped(self, thread_num):
        self.connection_count -= 1

    # NNTP Connection - Segment completed.
    def segComplete(self, seg):
        if ( seg == None ): return

        if ( seg.data ): 
            data_size = len("".join(seg.data))

            if ( (time.time() - self.speedTime) > 1 ):
                self.status.kbps = self.speedCounter
                self.speedCounter = 0
                self.speedTime = time.time()
            else:
                self.speedCounter += (data_size/1024)

            self.cache.append(seg)
        mt.log.debug("Segment Complete: " + seg.msgid)

    # NNTP Connection - Download of segment failed.
    def segFailed(self, seg):
        if ( seg == None ): return

        if ( seg.aborted() ):
            mt.log.error("Segment Failed " + str(seg.retries+1) + " Times, Aborting. MsgID: " + seg.msgid)
            self.segments_aborted.append(seg.msgid)
            del seg
            return

        seg.retries += 1

        mt.log.error("Segment Failed: " + seg.msgid + " Retry: " + str(seg.retries))
        self.failed_queue.append(seg)

    # NNTP Connection - Next Segment
    def nextSeg(self):
        # if we're not running send an instant kill switch.
        if ( not self.running ): return -1

        # try to a segment from main queue or failed queue.
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
        for f in os.listdir(self.cache_path):
            ff = os.path.join(self.cache_path, f)
            if os.path.isfile(ff):
                os.remove(ff)
            
    def stopDownload(self):
        self.running = False
        del self.cache[:]
        del self.segment_list[:]
        del self.segments_finished[:]
        del self.segments_aborted[:]
        del self.segment_queue[:]
        del self.failed_queue[:]
        self.clearCache()

class NNTPConnection(Thread):
    def __init__(self, connection_number, server, port, username, password, ssl, nextSegFunc, onSegComplete = None, onSegFailed = None, onThreadStop = None, **kwds):
        Thread.__init__(self, **kwds)
        self.daemon = True

        # Settings
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

        # running flag.
        self.running = True

    def run(self):
        connection = None
        try:
            mt.log.debug("Thread " + str(self.connection_number) + " started.")
            start_time = time.time()

            seg = None
            while(self.running):

                try:
                    # Open either an SSL or regular NNTP connection.
                    if ( self.ssl ):
                        connection = NNTP_SSL(self.server, self.port, self.username, self.password, False, True)
                    else:
                        connection = NNTP(self.server, self.port, self.username, self.password, False, True)

                    while(self.running):
                        seg = self.nextSegFunc()
                        
                        # Out of segments, sleep for a second see if we get anymore.
                        if ( seg == None ):
                            time.sleep(1)
                            continue

                        # Download complete, bail.
                        if ( seg == -1 ): 
                            self.running = False
                            break

                        # Attempt to grab a segment.
                        try:
                            #seg.data = connection.getrawresp( "BODY <%s>" % seg.msgid, seg.lastTry() )
                            #if ( self.onSegComplete ): self.onSegComplete(seg)
                            resp, nr, id, list = connection.body("<%s>" % seg.msgid)
                            if resp.startswith("2"):
                                seg.data = list
                                if ( self.onSegComplete ): self.onSegComplete(seg)
                            else:
                                self.onSegFailed(seg)

                        except NNTPReplyError:
                            mt.log.error("NNTP reply error.")
                            if ( self.onSegFailed ): self.onSegFailed(seg)

                        except Exception as inst:
                            if ( self.onSegFailed ): self.onSegFailed(seg)
                            mt.log.error("Error getting segment: " + str(inst))

                # If a connection error occurs, it will loop and try to open another connection.
                except Exception as inst:
                    self.onSegFailed(seg)
                    mt.log.error("Connection error: " + str(inst.args))

                finally:
                    try: 
                        if ( connection ): connection.quit()
                    except: 
                        pass

            end_time = time.time()
            mt.log.debug("Thread " + str(self.connection_number) + " stopped after " + str(end_time-start_time) + " seconds.")

        # A thread error is fatal, another thread won't be opened. These shouldn't occur.
        except Exception as inst:
            mt.log.error("Thread Error: " + str(inst.args))

        finally:
            try: 
                if ( self.onThreadStop ): self.onThreadStop(self.connection_number)
                if ( connection ): connection.quit()
            except: 
                pass
            del connection
