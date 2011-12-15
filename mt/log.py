"""
 * metaTower v0.4.0
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew MacIntyre
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
                    time.sleep(1)
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

# DEBUG       10
# INFO        20
# WARNING     30
# ERROR       40
# CRITICAL    50
# FATAL       50
log_level = 0
log_thread = LogThread(log_dir)
log_thread.start()

def setLevel(value):
    global log_level
    log_level = value

def getName():
    global log_thread
    source = mt.utils.getSource(3).split(".")[0]
    if ( names.has_key(source) ):
        return names[source]
    return source

def debug(text):
    global log_thread, log_level
    if ( log_level > 10 ): return
    log_thread.addItem(getName(), "DEBUG", text)

def info(text):
    global log_thread
    if ( log_level > 20 ): return
    log_thread.addItem(getName(), "INFO", text)

def warning(text):
    global log_thread
    if ( log_level > 30 ): return
    log_thread.addItem(getName(), "WARNING", text)

def error(text):
    global log_thread
    if ( log_level > 40 ): return
    log_thread.addItem(getName(), "ERROR", text)

def critical(text):
    global log_thread
    log_thread.addItem(getName(), "CRITICAL", text)

def fatal(text):
    global log_thread
    log_thread.addItem(getName(), "FATAL", text)

def profile(text):
    global log_thread
    log_thread.addItem("profile", "PROFILE", text)

def alias(source, name):
    global names
    names[source] = name