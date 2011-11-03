import sys, os, logging, urllib, time, socket
from threading import Thread
from dlmanager.NZB import NZBParser
from dlmanager.NZB.nntplib2 import NNTP_SSL,NNTPError,NNTP
from dlmanager.NZB.TextDecoder import ArticleDecoder

log = logging.getLogger("NZBClient")
hdlr = logging.FileHandler('packages/dlmanager/nzb.log')
log.addHandler(hdlr)

thread_count = []
Running = False

class StatusReport(object):
	def __init__(self):
		self.total_bytes = 0
		self.current_bytes = 0
		self.completed = False
		self.error_occured = False
		self.start_time = 0
		self.file_name = ""

class NZBClient():
    def __init__(self, nzbFile, save_to, nntpServer, nntpPort, nntpUser=None, nntpPassword=None, nntpSSL=False, nntpConnections=5):
        global Running
        realFile = urllib.urlopen( nzbFile )

        self.nntpServer = nntpServer
        self.nntpUser = nntpUser
        self.nntpPort = nntpPort
        self.nntpPassword = nntpPassword
        self.nntpSSL = nntpSSL
        self.nntpConnections = nntpConnections

        self.nzb = NZBParser.parse(realFile)
        self.save_to = save_to

        self.status = StatusReport()
        self.status.file_name = nzbFile
        self.status.total_bytes = self.nzb.size

        self.completed = False
        self.cache = []
        self.connection_count = 0

        self.SegmentList = []
        self.FinishedSegments = []
        self.SegmentQueue = []
        self.FailedSegments = [] 
        self.running = True
        self.allDecoded = False

    def start(self):
        global Running, thread_count

        Running = True

        tasks = []
        self.status.start_time = time.time()
        start_time = time.time()

        #segments = []
        for file in self.nzb.files:
            for seg in file.segments:
                #segments.append(seg)
                self.SegmentList.append(seg.msgid)
                self.SegmentQueue.append(seg)
        seg_count = len(self.SegmentQueue)

        # start the connections.
        for a in range(0, self.nntpConnections):
            thread = NNTPConnection(a, self.nntpServer, self.nntpPort, self.nntpUser, self.nntpPassword, self.nntpSSL, self.nextSeg, self.segComplete, self.segFailed, self.threadStopped)
            thread.start()
            self.connection_count += 1

        # start the article decoder.
        self.articleDecoder = ArticleDecoder(self.decodeNextSeg, self.save_to, self.decodeFinished, self.decodeSuccess, self.segFailed)
        self.articleDecoder.start()

    def decodeNextSeg(self):
        seg = None
        try:
            seg = self.cache.pop()
        except:
            pass
        if ( seg == None ) and ( self.allDecoded ):
            return -1
        return seg

    def decodeFinished(self):
        self.status.completed = True
        
    def decodeSuccess(self, seg):
        self.FinishedSegments.append(seg.msgid) 
        if ( len(self.FinishedSegments) >= len(self.SegmentList) ):
            self.allDecoded = True     

    def nextSeg(self):
        QueueEmpty = False
        FailedEmpty = False

        seg = None
        try:
            seg = self.SegmentQueue.pop()
        except:
            QueueEmpty = True
            pass

        if ( QueueEmpty ):
            try:
                seg = self.FailedSegments.pop()
            except:
                FailedEmpty = True
                pass

        # We're all outta segments.
        if ( FailedEmpty ):
            self.completed = True

        return seg

    def threadStopped(self, thread_num):
        self.connection_count -= 1

    def segComplete(self, seg):
        if ( seg == None ): return
        if ( seg.data ): 
            self.status.current_bytes += len(seg.data)
            self.cache.append(seg)
        log.debug("Segment Complete: " + seg.msgid)

    def segFailed(self, seg):
        if ( seg == None ): return

        seg.retries += 1
        if ( seg.retries > 3 ):
            log.error("Segment Failed 3 Times, Aborting. MsgID: " + seg.msgid)
            return

        log.error("Segment Failed: " + seg.msgid + " Retry: " + str(seg.retries))
        self.FailedSegments.append(seg)

    def clearCache(self):
        for f in os.listdir("packages/dlmanager/cache"):
            ff = "packages/dlmanager/cache/" + f
            if os.path.isfile(ff):
                os.remove(ff)
            
    def stopDownload(self):
        global Running
        Running = False

class NNTPConnection(Thread):
    def __init__(self, connection_number, server, port, username, password, ssl, nextSegFunc, onSegComplete = None, onSegFailed = None, onThreadStop = None, **kwds):
        Thread.__init__(self, **kwds)
        self.daemon = True

        self.connection_number = connection_number
        self.connection_cache = []
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.segments = []
        self.ssl = ssl
        self.nextSegFunc = nextSegFunc
        self.onSegComplete = onSegComplete
        self.onSegFailed = onSegFailed
        self.onThreadStop = onThreadStop
        self.running = True

    def addSegment(self, seg):
        self.segments.append(seg)

    def run(self):
        global Running, thread_count
        thread_count.append(0)

        connection = None
        cache = {}

        try:
            log.debug("Thread " + str(self.connection_number) + " started.")
            start_time = time.time()

            seg = None
            while(self.running):
                if ( not Running ): break
                try:
                    if ( self.ssl ):
                        connection = NNTP_SSL(self.server, self.port, self.username, self.password, False, True)
                    else:
                        connection = NNTP(self.server, self.port, self.username, self.password, False, True)

                    while(self.running):
                        if ( not Running ): break

                        seg = self.nextSegFunc()
                        if ( seg == None ): 
                            self.running = False
                            break

                        try:
                            seg.data = connection.getrawresp( "BODY <%s>" % seg.msgid, (seg.retries == 2) )
                            if ( self.onSegComplete ): self.onSegComplete(seg)

                        except Exception as inst:
                            #if ( seg != None ): SegmentQueue.append(seg)
                            if ( self.onSegFailed ): self.onSegFailed(seg)
                            log.debug("Connection Error: " + str(inst.args))
                            #break

                            #If ( not timed_out_seg ):
                            #    seg = SegmentQueue.pop() 
                            #else:
                            #    seg = timed_out_seg
                            #    timed_out_seg = False

                            

                            #cache[str(seg)] = data
                            #if ( self.onDataReceived ): self.onDataReceived(len(data))

                            #if ( len(cache) > 25 ):
                            #    self.writeCache(cache)
                            #    del cache
                            #    cache = {}
                        #except IndexError:
                        #    raise

                        #except socket.timeout:
                        #    log.debug("Socket timed out, retrying timed out segment.")
                       #     timed_out_seg = seg

                except Exception as inst:
                    self.onSegFailed(seg)
                    log.debug("Thread error: " + str(inst.args))
                finally:
                    try: 
                        if ( connection ): connection.quit()
                    except: 
                        pass

            #if ( len(cache) > 0 ):
            #    self.writeCache(cache)

            #self.connection_cache.close()

            end_time = time.time()
            log.debug("Thread " + str(self.connection_number) + " stopped after " + str(end_time-start_time) + " seconds.")
            thread_count.pop()

        except Exception as inst:
            log.debug("Thread Error: " + str(inst.args))

        finally:
            try: 
                if ( self.onThreadStop ): self.onThreadStop(self.connection_number)
                if ( connection ): connection.quit()
            except: 
                pass
            del connection
            del cache
            
    
    def parseSegment(self, lines):
        for headerStop in xrange( 0, len(lines) ):
            if lines[headerStop] == "" : break
        for bodyStart in xrange( headerStop, len(lines) ):
            if lines[bodyStart] != "" : break;
        return ( lines[0:headerStop], lines[bodyStart:len(lines)] )
