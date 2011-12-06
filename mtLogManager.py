"""
 * metaTower v0.3.5
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew W. MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import logging, mtMisc, threading, time, os

class LogWriteThread(threading.Thread):
    class LogItem:
        def __init__(self, source, level, data):
            self.source = source
            self.level = level
            self.data = data

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = []

    def run(self):
        file_handles = {}
        try:
            while True:
                try:
                    item = self.queue.pop()
                    if ( not file_handles.has_key(item.source) ):
                        file_handles[item.source] = open(os.path.join("logs", item.source + ".log"), "w")
                    file_handles[item.source].write(item.level + ": " + item.data + "\n")
                    file_handles[item.source].flush()
                except:
                    time.sleep(0.5)
        finally:
            for f in file_handles: 
                file_handles[f].close()

    def addItem(self, source, level, data):
        i = self.LogItem(source,level,data)
        self.queue.append(i)

class LogManager:
    def __init__(self):
        self.logThread = LogWriteThread()
        self.logThread.start()
        mtMisc.mkdir("logs")
        #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', filename='metaTower.log', filemode='w')
        #self.log = logging.getLogger("metatower")

    def getSource(self):
        return mtMisc.getSource(3).split(".")[0]

    def debug(self, text):
        self.logThread.addItem(self.getSource(), "DEBUG", text)
    
    def error(self, text):
        self.logThread.addItem(self.getSource(), "ERROR", text)
    
    def info(self, text):
        self.logThread.addItem(self.getSource(), "INFO", text)
