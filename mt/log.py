"""
 * metaTower v0.4.0
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew W. MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import logging, threading, time, os, mt

class LogThread(threading.Thread):
    class LogItem:
        def __init__(self, source, level, data):
            self.source = source
            self.level = level
            self.data = data

    def __init__(self, log_dir):
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = []
        self.log_dir = log_dir

    def run(self):
        file_handles = {}
        try:
            while True:
                try:
                    item = self.queue.pop()
                    if ( not file_handles.has_key(item.source) ):
                        file_handles[item.source] = open(os.path.join(self.log_dir, item.source + ".log"), "w")
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

log_dir = "logs"
names = {};
mt.utils.rmdir(log_dir)
mt.utils.mkdir(log_dir)

log_thread = LogThread(log_dir)
log_thread.start()

def getName():
    global log_thread
    source = mt.utils.getSource(3).split(".")[0]
    if ( names.has_key(source) ):
        return names[source]
    return source

def debug(text):
    global log_thread
    log_thread.addItem(getName(), "DEBUG", text)

def error(text):
    global log_thread
    log_thread.addItem(getName(), "ERROR", text)

def info(text):
    global log_thread
    log_thread.addItem(getName(), "INFO", text)

def alias(source, name):
    global names
    names[source] = name
