#!/usr/bin/env python

from clock import clock
from download_bt1 import parse_params, BT1Download, createPeerID, seed, get_usage, get_response, _failfunc
from RawServer import RawServer
from natpunch import UPnP_test
from bencode import bencode, bdecode
from threading import Event
from os.path import abspath
from sha import sha
from time import strftime
from threading import Thread
import os

class TorrentThread(Thread):
    def __init__(self, filename, fileFunc, onUpdate, onFinished, onError, doneflag):
        Thread.__init__(self)
        self.daemon = True

        self.filename = filename
        self.fileFunc = fileFunc
        self.onUpdate = onUpdate
        self.onFinished = onFinished
        self.onError = onError
        self.doneflag = doneflag

        self.btDownload = None

    def download(self, params, filefunc, statusfunc, finfunc, errorfunc, doneflag, cols,
                 pathFunc = None, presets = {}, exchandler = None,
                 failed = _failfunc, paramfunc = None):

        try:
            config = parse_params(params, presets)
        except ValueError, e:
            failed('error: ' + str(e) + '\nrun with no args for parameter explanations')
            return
        if not config:
            errorfunc(get_usage())
            return
        
        myid = createPeerID()
        seed(myid)

        rawserver = RawServer(doneflag, config['timeout_check_interval'],
                              config['timeout'], ipv6_enable = config['ipv6_enabled'],
                              failfunc = failed, errorfunc = exchandler)

        upnp_type = UPnP_test(config['upnp_nat_access'])
        try:
            listen_port = rawserver.find_and_bind(config['minport'], config['maxport'],
                            config['bind'], ipv6_socket_style = config['ipv6_binds_v4'],
                            upnp = upnp_type, randomizer = config['random_port'])
        except socketerror, e:
            failed("Couldn't listen - " + str(e))
            return

        response = get_response(config['responsefile'], config['url'], failed)
        if not response:
            return

        infohash = sha(bencode(response['info'])).digest()

        self.btDownload = BT1Download(statusfunc, finfunc, errorfunc, exchandler, doneflag,
                        config, response, infohash, myid, rawserver, listen_port)

        if not self.btDownload.saveAs(filefunc):
            return

        if pathFunc:
            pathFunc(self.btDownload.getFilename())

        hashcheck = self.btDownload.initFiles(old_style = True)
        if not hashcheck:
            return
        if not self.btDownload.startEngine():
            return

        self.btDownload.startRerequester()
        self.btDownload.autoStats()
        statusfunc(activity = 'connecting to peers')

        if paramfunc:
            paramfunc({ 'max_upload_rate' : self.btDownload.setUploadRate,  # change_max_upload_rate(<int KiB/sec>)
                        'max_uploads': self.btDownload.setConns, # change_max_uploads(<int max uploads>)
                        'listen_port' : listen_port, # int
                        'peer_id' : myid, # string
                        'info_hash' : infohash, # string
                        'start_connection' : self.btDownload._startConnection, # start_connection((<string ip>, <int port>), <peer id>)
                        })

        rawserver.listen_forever(self.btDownload.getPortHandler())
        self.btDownload.shutdown()

    def run(self):
        self.download([self.filename], self.fileFunc, self.onUpdate, self.onFinished, self.onError, self.doneflag, None)

    def stop(self):
        self.btDownload.shutdown()

class TorrentClient:
    def __init__(self):
        self.done = False
        self.downloading = False
        self.file = ''
        self.filename = ""
        self.realFilename = None
        self.percentDone = ''
        self.timeEst = ''
        self.downloadTo = ''
        self.downRate = ''
        self.upRate = ''
        self.shareRating = ''
        self.seedStatus = ''
        self.peerStatus = ''
        self.errors = []
        self.last_update_time = -1
        self.torrentThread = None
        self.doneflag = Event()
        self.saveto = "files/downloads/torrent/"

    def start(self, filename):
        self.filename = filename
        self.torrentThread = TorrentThread(filename,
            self.fileFunc,
            self.onUpdate,
            self.onFinished,
            self.onError,
            self.doneflag)
        self.downloading = True
        self.torrentThread.start()

    def stopDownload(self):
        self.downloading = False
        self.torrentThread.stop()

    def onFinished(self):
        self.downloading = False
        self.done = True
        self.percentDone = '100'
        self.timeEst = 'Download Succeeded!'
        self.downRate = ''

    def onFailed(self):
        self.downloading = False
        self.done = True
        self.percentDone = '0'
        self.timeEst = 'Download Failed!'
        self.downRate = ''

    def onError(self, errormsg):
        self.errors.append(errormsg)

    def onUpdate(self, dpflag = Event(), fractionDone = None, timeEst = None, 
            downRate = None, upRate = None, activity = None,
            statistics = None,  **kws):

        if self.last_update_time + 0.1 > clock() and fractionDone not in (0.0, 1.0) and activity is not None:
            return
        self.last_update_time = clock()        
        if fractionDone is not None:
            self.percentDone = str(float(int(fractionDone * 1000)) / 10)
        if timeEst is not None:
            self.timeEst = self.hours(timeEst)
        if activity is not None and not self.done:
            self.timeEst = activity
        if downRate is not None:
            self.downRate = '%.1f kB/s' % (float(downRate) / (1 << 10))
        if upRate is not None:
            self.upRate = '%.1f kB/s' % (float(upRate) / (1 << 10))
        if statistics is not None:
           if (statistics.shareRating < 0) or (statistics.shareRating > 100):
               self.shareRating = 'oo  (%.1f MB up / %.1f MB down)' % (float(statistics.upTotal) / (1<<20), float(statistics.downTotal) / (1<<20))
           else:
               self.shareRating = '%.3f  (%.1f MB up / %.1f MB down)' % (statistics.shareRating, float(statistics.upTotal) / (1<<20), float(statistics.downTotal) / (1<<20))
           if not self.done:
              self.seedStatus = '%d seen now, plus %.3f distributed copies' % (statistics.numSeeds,0.001*int(1000*statistics.numCopies))
           else:
              self.seedStatus = '%d seen recently, plus %.3f distributed copies' % (statistics.numOldSeeds,0.001*int(1000*statistics.numCopies))
           self.peerStatus = '%d seen now, %.1f%% done at %.1f kB/s' % (statistics.numPeers,statistics.percentDone,float(statistics.torrentRate) / (1 << 10))   

        dpflag.set()   

    def fileFunc(self, default, size, saveas, dir):
        self.file = '%s (%.1f MB)' % (default, float(size) / (1 << 20))
        if saveas != '':
            default = saveas
        self.downloadTo = abspath(default)
        self.realFilename = default
        return os.path.join(self.saveto, default)

    def hours(self, n):
        if n == 0:
            return 'complete!'
        try:
            n = int(n)
            assert n >= 0 and n < 5184000  # 60 days
        except:
            return '<unknown>'

        m, s = divmod(n, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return '%d hour %02d min %02d sec' % (h, m, s)
        else:
            return '%d min %02d sec' % (m, s)
